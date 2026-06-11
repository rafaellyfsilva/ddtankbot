import json
from pathlib import Path

import pyautogui

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

TEMPLATE_DIR = Path(__file__).with_name("screenshots") / "backpack"
TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)


def prompt_region() -> tuple[int, int, int, int]:
    print("\nMova o mouse para o canto superior esquerdo da área e pressione Enter.")
    input("Enter para capturar o primeiro ponto...")
    x1, y1 = pyautogui.position()
    print(f"Ponto superior esquerdo: ({x1}, {y1})")

    print("\nMova o mouse para o canto inferior direito da área e pressione Enter.")
    input("Enter para capturar o segundo ponto...")
    x2, y2 = pyautogui.position()
    print(f"Ponto inferior direito: ({x2}, {y2})")

    left = min(x1, x2)
    top = min(y1, y2)
    right = max(x1, x2)
    bottom = max(y1, y2)
    return left, top, right - left, bottom - top


def main() -> None:
    print("Template capture helper")
    print("Os templates serão salvos em:")
    print(f"  {TEMPLATE_DIR}\n")

    name = input("Nome do template (ex: slot_empty, slot_full, icon_esmeralda): ").strip()
    if not name:
        print("Nome inválido. Saindo.")
        return

    region = prompt_region()
    print(f"Capturando região: {region}")

    screenshot = pyautogui.screenshot(region=region)
    output_path = TEMPLATE_DIR / f"{name}.png"
    screenshot.save(output_path)

    metadata = {
        "name": name,
        "path": str(output_path),
        "region": region,
    }
    with open(TEMPLATE_DIR / f"{name}.json", "w", encoding="utf-8") as fh:
        json.dump(metadata, fh, indent=2)

    print(f"\nTemplate salvo em: {output_path}")
    print("Se quiser, capture mais templates usando o mesmo script.")


if __name__ == "__main__":
    main()
