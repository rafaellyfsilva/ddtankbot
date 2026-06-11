import time
from pathlib import Path

from ddtank import ActionArea, capture_action_area, load_action_area
from screen_recognition import ScreenState


def ensure_folder(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def main() -> None:
    area = load_action_area()
    if area is None:
        print("Área de ação não configurada. Execute ddtank.py primeiro.")
        return

    screenshots_dir = Path(__file__).with_name("screenshots")
    print("Treinamento de reconhecimento de tela")
    print("Navegue para cada tela dentro do jogo e pressione Enter para salvar uma captura.")
    print("Pressione Ctrl+C para sair a qualquer momento.")

    states = [
        ScreenState.LOBBY_INICIAL,
        ScreenState.COMO_JOGAR,
        ScreenState.DD_MINERACAO,
        ScreenState.CAMPO_DE_MINERACAO,
        ScreenState.HOMEM_DE_NEGOCIOS,
    ]

    while True:
        for state in states:
            target_dir = screenshots_dir / state.value
            ensure_folder(target_dir)

            input(f"Coloque o jogo na tela '{state.value}' e pressione Enter para capturar...")
            screenshot = capture_action_area(area)
            filename = target_dir / f"{int(time.time())}.png"
            screenshot.save(filename)
            print(f"Captura salva: {filename}\n")

        again = input("Deseja gravar mais exemplos? [s/N]: ").strip().lower()
        if again not in ("s", "sim"):
            break

    print("Treinamento finalizado. Use as imagens salvas em screenshots/<estado>/ para reconhecimento.")


if __name__ == "__main__":
    main()
