import json
import tkinter as tk
import ctypes
import time
from typing import Optional
from dataclasses import dataclass
from pathlib import Path

import pyautogui

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

CONFIG_PATH = Path(__file__).with_name("action_area_config.json")
DEFAULT_WIDTH = 997
DEFAULT_HEIGHT = 600
WINDOW_CONFIG_PATH = Path(__file__).with_name("window_config.json")
WINDOW_TITLE: Optional[str] = None


@dataclass
class ActionArea:
    left: int
    top: int
    width: int
    height: int
    wake_rel_x: float = 0.95
    wake_rel_y: float = 0.05

    def contains(self, x: int, y: int) -> bool:
        return self.left <= x <= self.left + self.width and self.top <= y <= self.top + self.height

    def to_dict(self) -> dict:
        return {
            "left": self.left,
            "top": self.top,
            "width": self.width,
            "height": self.height,
            "wake_rel_x": self.wake_rel_x,
            "wake_rel_y": self.wake_rel_y,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ActionArea":
        return cls(
            left=int(data["left"]),
            top=int(data["top"]),
            width=int(data["width"]),
            height=int(data["height"]),
            wake_rel_x=float(data.get("wake_rel_x", 0.95)),
            wake_rel_y=float(data.get("wake_rel_y", 0.05)),
        )


def save_config(data: dict, path: Path = CONFIG_PATH) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Configuração gravada em: {path}")


def save_window_title(title: str, path: Path = WINDOW_CONFIG_PATH) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump({"window_title": title}, f, indent=2)
    print(f"Título da janela gravado em: {path}")


def load_window_title(path: Path = WINDOW_CONFIG_PATH) -> Optional[str]:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("window_title")


def load_config(path: Path = CONFIG_PATH) -> dict | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def prompt_template_size() -> tuple[int, int]:
    use_default = input(
        f"Usar tamanho padrão do molde {DEFAULT_WIDTH}x{DEFAULT_HEIGHT}? [Enter=s / n]: "
    ).strip().lower()
    if use_default in ("", "s", "sim"):
        return DEFAULT_WIDTH, DEFAULT_HEIGHT

    width = int(input("Largura do molde (px): ").strip())
    height = int(input("Altura do molde (px): ").strip())
    return width, height


def show_visual_mold(width: int, height: int, resizable: bool = True, show_label: bool = True) -> ActionArea:
    root = tk.Tk()
    root.title("Molde de calibração")
    root.geometry(f"{width}x{height}+100+100")
    root.overrideredirect(not show_label)
    root.attributes("-topmost", True)
    root.resizable(resizable, resizable)
    try:
        root.attributes("-alpha", 0.18)
    except Exception:
        pass

    frame = tk.Frame(root, bg="#ff0000", bd=0 if not show_label else 4, relief="solid")
    frame.pack(fill="both", expand=True)
    if show_label:
        label = tk.Label(
            frame,
            text=(
                "Arraste e redimensione este molde sobre o jogo.\n"
                "Quando estiver alinhado, pressione Enter no terminal."
            ),
            bg="#000000",
            fg="#ffffff",
            font=("Arial", 10, "bold"),
            justify="center",
        )
        label.place(relx=0.5, rely=0.5, anchor="center")

    def start_move(event: tk.Event) -> None:
        root._drag_start_x = event.x
        root._drag_start_y = event.y

    def on_move(event: tk.Event) -> None:
        x = root.winfo_x() + event.x - root._drag_start_x
        y = root.winfo_y() + event.y - root._drag_start_y
        root.geometry(f"+{x}+{y}")

    frame.bind("<Button-1>", start_move)
    frame.bind("<B1-Motion>", on_move)
    if show_label:
        label.bind("<Button-1>", start_move)
        label.bind("<B1-Motion>", on_move)

    print("Arraste o molde transparente para encaixar sobre a área do jogo.")
    print("Quando estiver pronto, pressione Enter no terminal.")
    input()

    root.update_idletasks()
    left = root.winfo_x()
    top = root.winfo_y()
    width = root.winfo_width()
    height = root.winfo_height()
    root.destroy()
    print(f"Posição do molde registrada em: ({left}, {top}, {width}x{height})")
    return ActionArea(left=left, top=top, width=width, height=height)


def define_action_area_template() -> ActionArea:
    print("Defina o molde da janela do jogo.")
    width, height = prompt_template_size()
    area = show_visual_mold(width, height)
    save_config({"mode": "template", **area.to_dict()})
    print("Molde registrado com sucesso.")
    return area


def define_action_area_manual() -> ActionArea:
    print("Defina a área de ação do bot para padronizar coordenadas.")
    print("1) Mova o mouse para o canto superior esquerdo da área desejada.")
    input("Pressione Enter quando estiver pronto...")
    x1, y1 = pyautogui.position()
    print(f"Canto superior esquerdo definido em: ({x1}, {y1})")

    print("2) Mova o mouse para o canto inferior direito da área desejada.")
    input("Pressione Enter quando estiver pronto...")
    x2, y2 = pyautogui.position()
    print(f"Canto inferior direito definido em: ({x2}, {y2})")

    left = min(x1, x2)
    top = min(y1, y2)
    right = max(x1, x2)
    bottom = max(y1, y2)
    width = right - left
    height = bottom - top

    if width <= 0 or height <= 0:
        raise ValueError("A área definida deve ter largura e altura maiores que zero.")

    area = ActionArea(left=left, top=top, width=width, height=height)
    save_config({"mode": "manual", **area.to_dict()})
    print(f"Área de ação salva: {area}")
    return area


def define_wake_click_point(area: ActionArea) -> ActionArea:
    print("Defina o ponto de clique que o bot usará para acordar a janela do jogo.")
    print("Mova o mouse para o ponto desejado dentro da área e pressione Enter.")
    input("Pressione Enter quando estiver pronto...")
    x, y = pyautogui.position()
    rel_x, rel_y = normalize_point(x, y, area)

    if not (0 <= rel_x <= 1 and 0 <= rel_y <= 1):
        print("Aviso: o ponto selecionado está fora da área de ação. O valor será salvo mesmo assim.")

    area.wake_rel_x = rel_x
    area.wake_rel_y = rel_y
    save_config({"mode": "manual", **area.to_dict()})
    print(f"Ponto de acordar salvo em coordenadas relativas: ({rel_x:.3f}, {rel_y:.3f})")
    return area


def load_action_area(path: Path = CONFIG_PATH) -> ActionArea | None:
    config = load_config(path)
    if config is None:
        return None
    return ActionArea.from_dict(config)


def normalize_point(x: int, y: int, area: ActionArea) -> tuple[float, float]:
    rel_x = (x - area.left) / area.width
    rel_y = (y - area.top) / area.height
    return rel_x, rel_y


def denormalize_point(rel_x: float, rel_y: float, area: ActionArea) -> tuple[int, int]:
    x = area.left + int(rel_x * area.width)
    y = area.top + int(rel_y * area.height)
    return x, y


def click_relative(rel_x: float, rel_y: float, area: ActionArea, button: str = "left") -> None:
    # sempre tentar forçar foco na janela do jogo (ou acordar clicando na borda)
    try:
        force_focus_area(area)
    except Exception:
        pass

    x, y = denormalize_point(rel_x, rel_y, area)
    pyautogui.click(x, y, button=button)
    print(f"Clicado em ({x}, {y}) relativo ({rel_x:.3f}, {rel_y:.3f})")


def capture_action_area(area: ActionArea):
    # garantir foco/ressuscitar janela antes da captura
    try:
        force_focus_area(area)
        bx, by = denormalize_point(area.wake_rel_x, area.wake_rel_y, area)
        pyautogui.click(bx, by)
        time.sleep(0.2)
    except Exception:
        pass
    return pyautogui.screenshot(region=(area.left, area.top, area.width, area.height))


def force_focus_area(area: ActionArea) -> bool:
    """Tenta forçar o foco da janela do jogo.

    Estratégia:
    - se `WINDOW_TITLE` configurado, tenta focar pela string do título
    - caso contrário ou em falha, clica no ponto de acordar configurado.
    Retorna True se executou a ação (mesmo que não tenha certeza absoluta do foco).
    """
    global WINDOW_TITLE
    # 1) tentar foco pelo título, se disponível
    if WINDOW_TITLE:
        try:
            if focus_game_window(WINDOW_TITLE):
                return True
        except Exception:
            pass

    # 2) fallback: clicar no ponto de acordar configurado
    try:
        bx, by = denormalize_point(area.wake_rel_x, area.wake_rel_y, area)
        pyautogui.moveTo(bx, by, duration=0.08)
        pyautogui.click()
        time.sleep(0.12)
        return True
    except Exception:
        return False


def focus_game_window(title_substr: str) -> bool:
    """Tenta trazer a janela que contém `title_substr` para frente.

    Retorna True se encontrou e focou a janela, False caso contrário.
    """
    # Primeiro tente com pygetwindow (se disponível)
    try:
        import pygetwindow as gw

        wins = gw.getWindowsWithTitle(title_substr)
        if wins:
            win = wins[0]
            try:
                win.activate()
            except Exception:
                win.restore()
                win.activate()
            return True
    except Exception:
        pass

    # Fallback com Win32 API via ctypes: enumera janelas e compara título
    user32 = ctypes.windll.user32

    EnumWindows = user32.EnumWindows
    GetWindowTextW = user32.GetWindowTextW
    GetWindowTextLengthW = user32.GetWindowTextLengthW
    IsWindowVisible = user32.IsWindowVisible

    handles = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
    def foreach(hwnd, lparam):
        if IsWindowVisible(hwnd):
            length = GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                GetWindowTextW(hwnd, buff, length + 1)
                try:
                    if title_substr.lower() in buff.value.lower():
                        handles.append(hwnd)
                except Exception:
                    pass
        return True

    EnumWindows(foreach, 0)

    if not handles:
        return False

    hwnd = handles[0]
    # Mostrar e colocar em primeiro plano
    SW_SHOW = 5
    try:
        user32.ShowWindow(hwnd, SW_SHOW)
        user32.SetForegroundWindow(hwnd)
        return True
    except Exception:
        return False


def print_area(area: ActionArea) -> None:
    print("Área de ação:")
    print(f"  left: {area.left}")
    print(f"  top: {area.top}")
    print(f"  width: {area.width}")
    print(f"  height: {area.height}")


def main() -> None:
    config = load_config()
    area = None

    if config is not None:
        print("Configuração de área carregada do arquivo.")
        print_area(load_action_area())
        use_existing = input("Deseja usar a configuração existente? [S/n]: ").strip().lower()
        if use_existing in ("", "s", "sim"):
            area = load_action_area()

    if area is None:
        print("Nenhuma área definida ou optou por redefinir.")
        mode = input("Escolha o método [template/manual] (template padrão): ").strip().lower()
        if mode == "manual":
            area = define_action_area_manual()
        else:
            area = define_action_area_template()

    print_area(area)

    wake_choice = input(
        f"Ponto de acordar atual: ({area.wake_rel_x:.3f}, {area.wake_rel_y:.3f}). Deseja redefinir? [n/S]: "
    ).strip().lower()
    if wake_choice in ("s", "sim"):
        area = define_wake_click_point(area)

    # Carrega título da janela (opcional) e pergunta ao usuário se não existir
    global WINDOW_TITLE
    WINDOW_TITLE = load_window_title()
    if not WINDOW_TITLE:
        title = input("Título parcial da janela do jogo para focar automaticamente (Enter para pular): ").strip()
        if title:
            WINDOW_TITLE = title
            save_window_title(WINDOW_TITLE)

    print("\nExemplo de uso: clicar no centro da área de ação.")
    click_relative(0.5, 0.5, area)

    print("Capturando screenshot da área de ação...")
    screenshot = capture_action_area(area)
    screenshot_path = Path(__file__).with_name("action_area_snapshot.png")
    screenshot.save(screenshot_path)
    print(f"Screenshot salva em: {screenshot_path}")


if __name__ == "__main__":
    main()
