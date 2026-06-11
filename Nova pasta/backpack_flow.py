"""Fluxo de mochila para DDTank: navegação, calibração e contagem de slots."""

import json
import sys
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

import cv2
import numpy as np
import pyautogui

from ddtank import ActionArea, capture_action_area, click_relative, load_action_area, normalize_point, show_visual_mold
from button_coords_gen import DdMineracao
from vision import (
    convert_pil_to_cv2_color,
    load_template_color,
    match_template_score_color,
    preprocess_color,
)


@dataclass
class SlotRegion:
    """Região relativa para um slot da mochila."""
    rel_x: float
    rel_y: float
    width: float
    height: float
    name: str = ""


class SlotState(Enum):
    EMPTY = "vazio"
    UNKNOWN = "desconhecido"


BACKPACK_TEMPLATE_DIR = Path(__file__).with_name("screenshots") / "backpack"
BACKPACK_SLOT_CONFIG = BACKPACK_TEMPLATE_DIR / "slots.json"


def load_backpack_slot_config() -> Optional[dict]:
    if not BACKPACK_SLOT_CONFIG.exists():
        return None

    try:
        with BACKPACK_SLOT_CONFIG.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as exc:
        print(f"Falha ao carregar configuração de slots: {exc}")
        return None


def save_backpack_slot_config(config: dict) -> None:
    BACKPACK_SLOT_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    with BACKPACK_SLOT_CONFIG.open("w", encoding="utf-8") as fh:
        json.dump(config, fh, indent=2)
    print(f"Configuração de slots salva em: {BACKPACK_SLOT_CONFIG}")


def create_slot_regions_from_grid(config: dict, prefix: str) -> List[SlotRegion]:
    grid_left = float(config["grid_left"])
    grid_top = float(config["grid_top"])
    grid_width = float(config["grid_width"])
    grid_height = float(config["grid_height"])
    rows = int(config.get("rows", 4))
    cols = int(config.get("cols", 4))
    padding = float(config.get("padding", 0.08))

    cell_width = grid_width / cols
    cell_height = grid_height / rows
    inner_width = cell_width * (1.0 - 2 * padding)
    inner_height = cell_height * (1.0 - 2 * padding)

    regions: List[SlotRegion] = []
    for row in range(rows):
        for col in range(cols):
            rel_x = grid_left + col * cell_width + cell_width * padding
            rel_y = grid_top + row * cell_height + cell_height * padding
            name = f"{prefix}_{row + 1}_{col + 1}"
            regions.append(SlotRegion(rel_x, rel_y, inner_width, inner_height, name))

    return regions


def create_slot_regions_from_list(slot_list: list[dict]) -> List[SlotRegion]:
    regions: List[SlotRegion] = []
    for item in slot_list:
        regions.append(
            SlotRegion(
                float(item["rel_x"]),
                float(item["rel_y"]),
                float(item["width"]),
                float(item["height"]),
                item.get("name", "slot"),
            )
        )
    return regions


def add_slot_to_section_config(section: str, slot_region: SlotRegion, config: dict) -> dict:
    section_config = config.get(section, {})
    if "slots" not in section_config:
        section_config = {"slots": []}

    section_config["slots"].append(
        {
            "name": slot_region.name,
            "rel_x": slot_region.rel_x,
            "rel_y": slot_region.rel_y,
            "width": slot_region.width,
            "height": slot_region.height,
        }
    )
    config[section] = section_config
    return config


def prompt_slot_overlay_size(default_width: int = 120, default_height: int = 120) -> tuple[int, int]:
    text = input(
        f"Digite largura e altura do slot em pixels no formato WxH [Enter={default_width}x{default_height}]: "
    ).strip()
    if not text:
        return default_width, default_height

    parts = text.lower().replace(" ", "").split("x")
    if len(parts) != 2:
        print("Formato inválido. Usando tamanho padrão.")
        return default_width, default_height

    try:
        width = int(parts[0])
        height = int(parts[1])
        return max(20, width), max(20, height)
    except ValueError:
        print("Valores inválidos. Usando tamanho padrão.")
        return default_width, default_height


def define_individual_slot_region(area: ActionArea, section: str, slot_index: int, name_prefix: str) -> None:
    slot_name = f"{name_prefix}_{slot_index}"
    slot_label = "slot"
    if section == "vendor_minerals":
        slot_label = "minerio"
    elif section == "vendor_items":
        slot_label = "item"

    print(f"\n=== Calibração do {slot_label} {slot_index} em '{section}' ===")
    print("Abra a tela correta do jogo e deixe o item visível antes de continuar.")
    print("O molde inicia em 60x60 pixels sem barra de título.")
    print("Use a janela transparente para posicionar a área sobre o slot, depois pressione Enter.")

    overlay = show_visual_mold(60, 60, resizable=False, show_label=False)
    left_rel, top_rel = normalize_point(overlay.left, overlay.top, area)
    width_rel = overlay.width / area.width
    height_rel = overlay.height / area.height

    config = load_backpack_slot_config() or {}
    slot_region = SlotRegion(left_rel, top_rel, width_rel, height_rel, slot_name)
    config = add_slot_to_section_config(section, slot_region, config)
    save_backpack_slot_config(config)
    print(f"Slot '{slot_name}' calibrado e salvo.")


def define_vendor_mineral_slots(area: ActionArea) -> None:
    for slot_index in range(1, 5):
        define_individual_slot_region(area, "vendor_minerals", slot_index, "vendor_mineral")


def define_vendor_item_slots(area: ActionArea) -> None:
    for slot_index in range(1, 5):
        define_individual_slot_region(area, "vendor_items", slot_index, "vendor_item")


def get_slot_regions(area: ActionArea, section: str, default: dict, prefix: str) -> List[SlotRegion]:
    config = load_backpack_slot_config()
    if config is None or section not in config:
        print(f"Aviso: configuração de regiões '{section}' não encontrada. Usando valores padrão.")
        return create_slot_regions_from_grid(default, prefix)

    section_config = config[section]
    if isinstance(section_config, dict) and "slots" in section_config:
        return create_slot_regions_from_list(section_config["slots"])

    return create_slot_regions_from_grid(section_config, prefix)


def get_backpack_slot_regions(area: ActionArea) -> List[SlotRegion]:
    default = {
        "grid_left": 0.08,
        "grid_top": 0.18,
        "grid_width": 0.84,
        "grid_height": 0.72,
        "rows": 4,
        "cols": 4,
        "padding": 0.06,
    }
    return get_slot_regions(area, "backpack", default, "slot")


def get_vendor_mineral_regions(area: ActionArea) -> List[SlotRegion]:
    default = {
        "grid_left": 0.10,
        "grid_top": 0.46,
        "grid_width": 0.80,
        "grid_height": 0.12,
        "rows": 1,
        "cols": 4,
        "padding": 0.05,
    }
    return get_slot_regions(area, "vendor_minerals", default, "vendor_mineral")


def get_vendor_item_regions(area: ActionArea) -> List[SlotRegion]:
    default = {
        "grid_left": 0.10,
        "grid_top": 0.60,
        "grid_width": 0.80,
        "grid_height": 0.12,
        "rows": 1,
        "cols": 4,
        "padding": 0.05,
    }
    return get_slot_regions(area, "vendor_items", default, "vendor_item")


def define_region_grid(area: ActionArea, section: str, rows: int, cols: int, padding: float = 0.08) -> None:
    print(f"\n=== Calibração da região '{section}' ===")
    print("Abra a tela correta do jogo e deixe a região de slots visível antes de continuar.")
    input("Quando estiver pronto, pressione Enter...")

    print("Posicione o mouse no canto superior esquerdo da área de slots e pressione Enter.")
    input()
    x1, y1 = pyautogui.position()
    print(f"Canto superior esquerdo capturado: ({x1}, {y1})")

    print("Posicione o mouse no canto inferior direito da área de slots e pressione Enter.")
    input()
    x2, y2 = pyautogui.position()
    print(f"Canto inferior direito capturado: ({x2}, {y2})")

    left = min(x1, x2)
    top = min(y1, y2)
    width = abs(x2 - x1)
    height = abs(y2 - y1)

    if width == 0 or height == 0:
        print("Região inválida. Reinicie a calibração e tente novamente.")
        return

    left_rel, top_rel = normalize_point(left, top, area)
    right_rel, bottom_rel = normalize_point(left + width, top + height, area)
    grid_width = right_rel - left_rel
    grid_height = bottom_rel - top_rel

    config = load_backpack_slot_config() or {}
    config[section] = {
        "grid_left": left_rel,
        "grid_top": top_rel,
        "grid_width": grid_width,
        "grid_height": grid_height,
        "rows": rows,
        "cols": cols,
        "padding": padding,
    }
    save_backpack_slot_config(config)
    print("Calibração finalizada.")


def define_backpack_slot_grid(area: ActionArea) -> None:
    define_region_grid(area, "backpack", rows=4, cols=4, padding=0.06)


def define_backpack_slot_regions(area: ActionArea) -> None:
    for slot_index in range(1, 17):
        define_individual_slot_region(area, "backpack", slot_index, "slot")


def define_vendor_mineral_grid(area: ActionArea) -> None:
    define_region_grid(area, "vendor_minerals", rows=1, cols=4, padding=0.05)


def define_vendor_mineral_slots(area: ActionArea) -> None:
    for slot_index in range(1, 5):
        define_individual_slot_region(area, "vendor_minerals", slot_index, "vendor_mineral")


def define_vendor_item_grid(area: ActionArea) -> None:
    define_region_grid(area, "vendor_items", rows=1, cols=4, padding=0.05)


def define_vendor_item_slots(area: ActionArea) -> None:
    for slot_index in range(1, 5):
        define_individual_slot_region(area, "vendor_items", slot_index, "vendor_item")


def crop_slot(screen_gray: any, area: ActionArea, slot: SlotRegion) -> any:
    # coordinates must be relative to the captured screenshot (0-based)
    x1 = int(slot.rel_x * area.width)
    y1 = int(slot.rel_y * area.height)
    w = int(slot.width * area.width)
    h = int(slot.height * area.height)
    # safety: clamp to image bounds
    h = max(0, min(h, screen_gray.shape[0] - y1))
    w = max(0, min(w, screen_gray.shape[1] - x1))
    return screen_gray[y1 : y1 + h, x1 : x1 + w]


def load_backpack_templates(template_dir: Path = BACKPACK_TEMPLATE_DIR) -> Dict[str, Optional[any]]:
    templates: Dict[str, Optional[any]] = {
        "empty": load_template_color(template_dir / "slot_vazio.png"),
        "full": {},
    }

    for path in template_dir.glob("*.png"):
        if path.name == "slot_vazio.png":
            continue
        name = path.stem
        template = load_template_color(path)
        if template is not None:
            templates["full"][name] = template

    return templates


def save_debug_comparison(slot_crop: any, template: np.ndarray, output_path: Path) -> None:
    if slot_crop is None or template is None:
        return

    if len(slot_crop.shape) == 2:
        debug_vis = cv2.cvtColor(slot_crop, cv2.COLOR_GRAY2BGR)
    else:
        debug_vis = slot_crop.copy()

    if len(template.shape) == 2:
        template_vis = cv2.cvtColor(template, cv2.COLOR_GRAY2BGR)
    else:
        template_vis = template.copy()

    h = max(debug_vis.shape[0], template_vis.shape[0])
    w = debug_vis.shape[1] + template_vis.shape[1] + 10
    combined = np.zeros((h, w, 3), dtype=np.uint8)
    combined[: debug_vis.shape[0], : debug_vis.shape[1]] = debug_vis
    combined[: template_vis.shape[0], debug_vis.shape[1] + 10 : debug_vis.shape[1] + 10 + template_vis.shape[1]] = template_vis

    cv2.putText(combined, "slot_crop", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(combined, "template", (debug_vis.shape[1] + 20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.imwrite(str(output_path), combined)


def scan_slot(
    slot_crop: any,
    templates: Dict[str, Optional[any]],
    threshold: float = 0.65,
    debug: bool = False,
    slot_name: str = "",
) -> str:
    """Retorna o nome do template encontrado (ex: 'carvao', 'ferro') ou 'vazio'.
    Se nenhum template atingir o threshold (0.70), considera o slot vazio."""
    # Recorta top 75% do slot (remove barra de quantidade no rodapé)
    item_h = int(slot_crop.shape[0] * 0.75)
    item_area = slot_crop[:item_h, :]

    if debug:
        print(f"[DEBUG] Slot '{slot_name}' crop: {slot_crop.shape} -> item area: {item_area.shape}")

    best_score = 0.0
    best_template_name = None
    best_template = None

    full_templates = templates.get("full", {})
    for name, full_template in full_templates.items():
        score = match_template_score_color(item_area, full_template)
        if debug:
            print(f"[DEBUG]   template '{name}': score={score:.3f}")
        if score > best_score:
            best_score = score
            best_template_name = name
            best_template = full_template

    if best_score < threshold:
        if debug:
            print(f"[DEBUG]   melhor score {best_score:.3f} < {threshold} -> tratando como VAZIO")
        return "vazio"

    if debug:
        print(f"[DEBUG]   best match for '{slot_name}': {best_template_name} (score={best_score:.3f})")

    if debug and best_template is not None:
        debug_folder = Path(__file__).with_name("debug_comparisons")
        debug_folder.mkdir(parents=True, exist_ok=True)
        save_debug_comparison(
            item_area,
            best_template,
            debug_folder / f"{slot_name}_best_{best_template_name}_{int(best_score * 1000)}.png",
        )

    return best_template_name


def reset_backpack_page(area: ActionArea, clicks: int = 3, delay: float = 0.6) -> None:
    """Retorna a mochila para a página inicial 1/4 clicando para a esquerda."""
    for _ in range(clicks):
        click_relative(DdMineracao.MOCHILA_LEFT.rel_x, DdMineracao.MOCHILA_LEFT.rel_y, area)
        time.sleep(delay)


def page_right(area: ActionArea, delay: float = 0.6) -> None:
    click_relative(DdMineracao.MOCHILA_RIGHT.rel_x, DdMineracao.MOCHILA_RIGHT.rel_y, area)
    time.sleep(delay)


def scan_region_group(
    area: ActionArea,
    templates: Dict[str, Optional[any]],
    slot_regions: List[SlotRegion],
    debug: bool = False,
    stop_at_empty: bool = False,
) -> tuple[Dict[str, str], bool]:
    """Escaneia slots e retorna (dict de slots, encontrou_vazio)."""
    screenshot = capture_action_area(area)
    if screenshot is None:
        return {}, False

    screen_bgr = convert_pil_to_cv2_color(screenshot)
    screen_bgr = preprocess_color(screen_bgr)
    if debug:
        debug_path = Path(__file__).with_name("debug_screenshots")
        debug_path.mkdir(parents=True, exist_ok=True)
        screenshot.save(debug_path / f"screen_page_{time.time_ns()}.png")

    results: Dict[str, str] = {}
    found_empty = False
    for slot in slot_regions:
        slot_crop = crop_slot(screen_bgr, area, slot)
        slot_result = scan_slot(
            slot_crop,
            templates,
            debug=debug,
            slot_name=slot.name,
        )
        results[slot.name] = slot_result
        if stop_at_empty and slot_result == "vazio":
            found_empty = True
            break
    return results, found_empty


def scan_backpack_page(
    area: ActionArea,
    templates: Dict[str, Optional[any]],
    slot_regions: List[SlotRegion],
    debug: bool = False,
) -> tuple[Dict[str, str], bool]:
    return scan_region_group(area, templates, slot_regions, debug=debug, stop_at_empty=True)


def scan_vendor_mineral_slots(area: ActionArea) -> Dict[str, str]:
    templates = load_backpack_templates()
    regions = get_vendor_mineral_regions(area)
    results, _ = scan_region_group(area, templates, regions, stop_at_empty=False)
    return results


def scan_vendor_item_slots(area: ActionArea) -> Dict[str, str]:
    templates = load_backpack_templates()
    regions = get_vendor_item_regions(area)
    results, _ = scan_region_group(area, templates, regions, stop_at_empty=False)
    return results


def prompt_before_scan() -> None:
    print("\nPrepare o jogo e deixe a janela em foco.")
    input("Pressione Enter para iniciar o scan...\n")


def return_backpack_to_start(area: ActionArea, clicks: int = 3, delay: float = 0.6) -> None:
    """Retorna para a primeira página da mochila com cliques à esquerda."""
    for _ in range(clicks):
        click_relative(DdMineracao.MOCHILA_LEFT.rel_x, DdMineracao.MOCHILA_LEFT.rel_y, area)
        time.sleep(delay)


def scan_all_backpack_pages(area: ActionArea, debug: bool = False) -> Dict:
    """Escaneia mochila até encontrar primeiro vazio. Retorna slots e cálculos de espaço."""
    templates = load_backpack_templates()
    slot_regions = get_backpack_slot_regions(area)
    all_slots: Dict[str, str] = {}
    total_slots_checked = 0
    total_empty_slots = 0
    first_empty_page = None
    first_empty_slot_index = None

    for page in range(1, 5):
        print(f"Verificando página {page}/4...")
        print(f"Página {page} - comparando {len(slot_regions)} slots contra {len(templates.get('full', {}))} templates...")
        page_results, found_empty = scan_backpack_page(area, templates, slot_regions, debug=debug)
        
        for slot_name, slot_result in page_results.items():
            all_slots[slot_name] = slot_result
            total_slots_checked += 1
            if slot_result == "vazio" and first_empty_page is None:
                first_empty_page = page
                first_empty_slot_index = total_slots_checked
                empty_in_this_page = len(page_results) - list(page_results.values()).index("vazio")
                total_empty_slots = empty_in_this_page
                # Adicionar slots vazios das páginas não verificadas
                remaining_pages = 4 - page
                total_empty_slots += remaining_pages * 16
                break
        
        if found_empty:
            break
        
        if page < 4:
            page_right(area)
            time.sleep(0.8)
    
    if first_empty_page is None:
        # Nenhum vazio encontrado, mochila cheia
        total_empty_slots = 0
    
    total_gold_capacity = total_empty_slots * 9999
    
    return_backpack_to_start(area)
    return {
        "slots": all_slots,
        "total_slots_checked": total_slots_checked,
        "total_empty_slots": total_empty_slots,
        "total_gold_capacity": total_gold_capacity,
        "first_empty_page": first_empty_page,
        "first_empty_slot_index": first_empty_slot_index,
    }


def summarize_backpack(results: Dict) -> Dict[str, int]:
    summary = {
        "total_slots_checked": results.get("total_slots_checked", 0),
        "total_empty_slots": results.get("total_empty_slots", 0),
        "total_gold_capacity": results.get("total_gold_capacity", 0),
    }
    return summary


def summarize_slots(results: Dict[str, str]) -> Dict[str, int]:
    summary = {"vazio": 0, "desconhecido": 0, "items": 0}
    for state in results.values():
        if state == "vazio":
            summary["vazio"] += 1
        elif state == "desconhecido":
            summary["desconhecido"] += 1
        else:
            summary["items"] += 1
    return summary


def pause_before_exit() -> None:
    print("\nScan concluído. Reveja as linhas acima e mantenha o terminal aberto.")
    input("Pressione Enter para sair...\n")


def capture_templates_from_backpack(area: ActionArea) -> None:
    """Captura templates dos itens diretamente da mochila do jogo.
    
    Recorta cada slot da página atual e pergunta o nome do item.
    Salva com o mesmo tamanho/fundo que o scan usa, garantindo scores altos.
    """
    print("\n=== CAPTURA DE TEMPLATES DA MOCHILA ===")
    print("Deixe a mochila aberta no jogo com os itens visíveis.")
    print("O bot vai recortar cada slot e perguntar o nome do item.\n")
    print("Itens conhecidos: carvao, diamante, esmeralda, ferro, gema_amarela, gold, ouro, rubi, safira")
    print("Digite 'v' para marcar vazio/pular, Enter para pular, 'q' para encerrar.\n")
    input("Pressione Enter quando estiver pronto...")

    screenshot = capture_action_area(area)
    if screenshot is None:
        print("Falha ao capturar screenshot.")
        return

    screen_bgr = convert_pil_to_cv2_color(screenshot)
    slot_regions = get_backpack_slot_regions(area)

    template_dir = BACKPACK_TEMPLATE_DIR
    template_dir.mkdir(parents=True, exist_ok=True)

    saved = 0
    for i, slot in enumerate(slot_regions):
        slot_crop = crop_slot(screen_bgr, area, slot)
        if slot_crop is None or slot_crop.size == 0:
            print(f"  Slot {i+1}: crop vazio, pulando.")
            continue

        # Remove rodapé com número de quantidade (top 75%)
        item_h = int(slot_crop.shape[0] * 0.75)
        template_crop = slot_crop[:item_h, :]

        # Salva preview para o usuário ver
        preview_path = template_dir / f"_preview_slot_{i+1}.png"
        cv2.imwrite(str(preview_path), template_crop)

        name = input(
            f"\nSlot {i+1}/16 - preview: {preview_path}"
            f"\n  Nome do item: "
        ).strip().lower()

        preview_path.unlink(missing_ok=True)

        if name in ("q", "quit", "sair"):
            print("Captura encerrada.")
            break
        if not name or name in ("v", "vazio", "pular"):
            print(f"  Slot {i+1} pulado.")
            continue

        save_path = template_dir / f"{name}.png"
        if save_path.exists():
            overwrite = input(f"  '{name}.png' já existe. Sobrescrever? [S/n]: ").strip().lower()
            if overwrite in ("n", "nao"):
                print(f"  Template '{name}' mantido.")
                continue

        cv2.imwrite(str(save_path), template_crop)
        saved += 1
        print(f"  Template '{name}' salvo! ({template_crop.shape[1]}x{template_crop.shape[0]})")

    print(f"\n{saved} templates salvos em: {template_dir}")


def main() -> None:
    area = load_action_area()
    if area is None:
        print("Área de ação não configurada. Execute ddtank.py primeiro.")
        return

    debug = "--debug" in sys.argv
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd in ("calibrate", "calibrar", "calibrate-backpack", "calibrar-mochila"):
            define_backpack_slot_grid(area)
            return
        if cmd in ("calibrate-backpack-slots", "calibrar-mochila-slots"):
            define_backpack_slot_regions(area)
            return
        if cmd in ("calibrate-vendor-minerals", "calibrar-minerais"):
            define_vendor_mineral_grid(area)
            return
        if cmd in ("calibrate-vendor-minerals-slots", "calibrar-minerais-slots"):
            define_vendor_mineral_slots(area)
            return
        if cmd in ("calibrate-vendor-minerals-and-backpack-slots", "calibrar-minerais-e-mochila-slots"):
            define_vendor_mineral_slots(area)
            define_backpack_slot_regions(area)
            return
        if cmd in ("calibrate-vendor-items", "calibrar-itens"):
            define_vendor_item_grid(area)
            return
        if cmd in ("calibrate-vendor-items-slots", "calibrar-itens-slots"):
            define_vendor_item_slots(area)
            return
        if cmd in ("capture-templates", "capturar-templates"):
            capture_templates_from_backpack(area)
            return
        if cmd in ("scan-backpack", "scan-mochila"):
            prompt_before_scan()
            results = scan_all_backpack_pages(area, debug=debug)
            summary = summarize_backpack(results)
            print(f"\nResumo da mochila: {summary}")
            return
        if cmd in ("scan-vendor-minerals", "scan-minerais"):
            prompt_before_scan()
            results = scan_vendor_mineral_slots(area)
            summary = summarize_slots(results)
            print(f"\nResumo dos slots de minério: {summary}")
            return
        if cmd in ("scan-vendor-items", "scan-itens"):
            prompt_before_scan()
            results = scan_vendor_item_slots(area)
            summary = summarize_slots(results)
            print(f"\nResumo dos slots de itens: {summary}")
            return

    print("Iniciando verificação da mochila (páginas 1 a 4)...")
    prompt_before_scan()
    results = scan_all_backpack_pages(area, debug=debug)
    summary = summarize_backpack(results)

    print("\nResumo da mochila:")
    print(f"  Slots verificados: {summary['total_slots_checked']}")
    print(f"  Slots vazios restantes: {summary['total_empty_slots']}")
    print(f"  Capacidade de gold: {summary['total_gold_capacity']} gold")
    print(f"  Primeira página vazia: {results.get('first_empty_page', 'Nenhuma')}")

    print("\nSlots encontrados:")
    for slot_name, slot_result in results["slots"].items():
        print(f"  {slot_name}: {slot_result}")

    pause_before_exit()


if __name__ == "__main__":
    main()
