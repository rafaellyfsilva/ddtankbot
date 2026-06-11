"""
Ferramenta interativa para mapear coordenadas dos botões do jogo.
Captura a posição do mouse ao pressionar Enter e converte em coordenadas relativas.
"""

import json
from pathlib import Path
from typing import Dict, Tuple

import pyautogui
import time

from ddtank import ActionArea, load_action_area


BUTTONS_CONFIG_PATH = Path(__file__).with_name("buttons_config.json")


class ButtonMapper:
    def __init__(self, area: ActionArea):
        self.area = area
        self.buttons: Dict[str, Dict[str, Tuple[float, float]]] = self.load_buttons()

    def load_buttons(self) -> Dict:
        """Carrega coordenadas salvas ou retorna dicionário vazio."""
        if BUTTONS_CONFIG_PATH.exists():
            with open(BUTTONS_CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_buttons(self) -> None:
        """Salva coordenadas em JSON."""
        with open(BUTTONS_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(self.buttons, f, indent=2, ensure_ascii=False)
        print(f"Coordenadas salvas em: {BUTTONS_CONFIG_PATH}")

    def pixel_to_relative(self, pixel_x: int, pixel_y: int) -> Tuple[float, float]:
        """Converte coordenadas de pixel para relativas (0.0 a 1.0)."""
        rel_x = (pixel_x - self.area.left) / self.area.width
        rel_y = (pixel_y - self.area.top) / self.area.height
        return round(rel_x, 3), round(rel_y, 3)

    def capture_button(self, screen_name: str, button_name: str) -> Tuple[float, float]:
        """
        Captura a coordenada de um botão interativamente.
        
        Args:
            screen_name: Nome da tela (ex: "lobby_inicial")
            button_name: Nome do botão (ex: "dd_mineracao")
        
        Returns:
            Tupla (rel_x, rel_y) com coordenadas relativas
        """
        print(f"\n{'='*60}")
        print(f"Mapeando botão: [{screen_name}] {button_name}")
        print(f"{'='*60}")
        print("\n1. Posicione o mouse SOBRE O BOTÃO na tela do jogo.")
        print("2. Pressione Enter para iniciar a captura. Você terá 3 segundos para posicionar o mouse (ou deixe já posicionado).\n")

        input("Pressione Enter para iniciar captura...")

        # Amostrar a posição do mouse por 3 segundos e usar a última posição estável
        samples = []
        duration = 3.0
        interval = 0.08
        iterations = int(duration / interval)
        print("Capturando posição do mouse nos próximos 3 segundos...")
        for i in range(iterations):
            pos = pyautogui.position()
            samples.append(pos)
            time.sleep(interval)

        # escolher a posição mais frequente (ou a última)
        pixel_x, pixel_y = samples[-1]
        rel_x, rel_y = self.pixel_to_relative(pixel_x, pixel_y)

        print(f"\n✓ Coordenada capturada:")
        print(f"  Pixel:   ({pixel_x}, {pixel_y})")
        print(f"  Relativa: ({rel_x}, {rel_y})")

        if screen_name not in self.buttons:
            self.buttons[screen_name] = {}
        self.buttons[screen_name][button_name] = [rel_x, rel_y]

        return rel_x, rel_y

    def capture_multiple_buttons(self, buttons_list: list) -> None:
        """
        Captura múltiplos botões em sequência.
        
        Args:
            buttons_list: Lista de tuplas (screen_name, button_name)
        """
        for screen_name, button_name in buttons_list:
            self.capture_button(screen_name, button_name)
            self.save_buttons()

            continue_input = input("\nDeseja continuar? [S/n]: ").strip().lower()
            if continue_input in ("n", "nao", "não"):
                print("Mapeamento interrompido.")
                break

    def print_buttons(self) -> None:
        """Exibe todos os botões mapeados."""
        if not self.buttons:
            print("Nenhum botão mapeado ainda.")
            return

        print("\n" + "="*60)
        print("BOTÕES MAPEADOS")
        print("="*60)

        for screen_name, buttons in self.buttons.items():
            print(f"\n[{screen_name}]")
            for btn_name, (rel_x, rel_y) in buttons.items():
                print(f"  {btn_name:30s} -> ({rel_x:.3f}, {rel_y:.3f})")

    def export_to_button_coords(self) -> None:
        """Exporta as coordenadas para o arquivo button_coords.py."""
        output = '''"""
Coordenadas dos botões do jogo DDTank.
Coordenadas em valores relativos (0.0 a 1.0) dentro do modal 997x600.
Auto-gerado pelo button_mapper.py
"""

from dataclasses import dataclass


@dataclass
class ButtonCoord:
    """Representa um botão com coordenadas relativas."""
    rel_x: float
    rel_y: float
    name: str = ""

    def __str__(self) -> str:
        return f"{self.name or 'Button'} ({self.rel_x:.3f}, {self.rel_y:.3f})"


'''

        for screen_name, buttons in self.buttons.items():
            class_name = "".join(word.capitalize() for word in screen_name.split("_"))
            output += f"# ============= TELA: {screen_name.upper()} =============\n"
            output += f"class {class_name}:\n"
            output += f'    """Coordenadas da tela {screen_name}."""\n'

            for btn_name, (rel_x, rel_y) in buttons.items():
                const_name = btn_name.upper()
                output += f'    {const_name} = ButtonCoord({rel_x}, {rel_y}, "{btn_name}")\n'

            output += "\n\n"

        output += "# ============= CONJUNTO DE TODAS AS COORDENADAS =============\n"
        output += "BUTTONS = {\n"

        for screen_name, buttons in self.buttons.items():
            class_name = "".join(word.capitalize() for word in screen_name.split("_"))
            output += f'    "{screen_name}": {{\n'
            for btn_name, _ in buttons.items():
                const_name = btn_name.upper()
                output += f'        "{btn_name}": {class_name}.{const_name},\n'
            output += "    },\n"

        output += "}\n"

        coord_file = Path(__file__).with_name("button_coords_gen.py")
        with open(coord_file, "w", encoding="utf-8") as f:
            f.write(output)

        print(f"\n✓ Coordenadas exportadas para: {coord_file}")


def main():
    area = load_action_area()
    if area is None:
        print("❌ Área de ação não configurada. Execute ddtank.py primeiro.")
        return

    mapper = ButtonMapper(area)

    print("\n" + "="*60)
    print("MAPEADOR DE BOTÕES - DDTank")
    print("="*60)

    while True:
        print("\nOpções:")
        print("1. Mapear novo botão")
        print("2. Mapear vários botões em sequência")
        print("3. Ver botões mapeados")
        print("4. Exportar para button_coords.py")
        print("5. Sair")

        choice = input("\nEscolha uma opção [1-5]: ").strip()

        if choice == "1":
            screen = input("Nome da tela (ex: lobby_inicial): ").strip()
            button = input("Nome do botão (ex: dd_mineracao): ").strip()
            mapper.capture_button(screen, button)
            mapper.save_buttons()

        elif choice == "2":
            print("\nInsira os botões a mapear (deixe em branco para terminar)")
            buttons_list = []
            while True:
                screen = input("Nome da tela (ou Enter para terminar): ").strip()
                if not screen:
                    break
                button = input("Nome do botão: ").strip()
                buttons_list.append((screen, button))

            if buttons_list:
                mapper.capture_multiple_buttons(buttons_list)

        elif choice == "3":
            mapper.print_buttons()

        elif choice == "4":
            mapper.export_to_button_coords()

        elif choice == "5":
            print("Saindo...")
            break

        else:
            print("Opção inválida.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback

        print("\nErro inesperado:")
        traceback.print_exc()
        input("Pressione Enter para encerrar...")
