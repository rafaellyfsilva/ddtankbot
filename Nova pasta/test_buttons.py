"""
Script para testar os botões mapeados e ajustar coordenadas se necessário.
"""

import json
import time
from pathlib import Path
from typing import Dict, Tuple

import pyautogui

from ddtank import ActionArea, click_relative, load_action_area

BUTTONS_CONFIG_PATH = Path(__file__).with_name("buttons_config.json")


class ButtonTester:
    def __init__(self, area: ActionArea):
        self.area = area
        self.buttons = self.load_buttons()

    def load_buttons(self) -> Dict:
        """Carrega os botões mapeados."""
        if BUTTONS_CONFIG_PATH.exists():
            with open(BUTTONS_CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_buttons(self) -> None:
        """Salva os botões atualizados."""
        with open(BUTTONS_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(self.buttons, f, indent=2, ensure_ascii=False)
        print("✓ Botões salvos.")

    def list_all_buttons(self) -> None:
        """Lista todos os botões mapeados."""
        if not self.buttons:
            print("Nenhum botão mapeado.")
            return

        print("\n" + "="*70)
        print("BOTÕES MAPEADOS")
        print("="*70)

        for screen_name, buttons in self.buttons.items():
            print(f"\n[{screen_name}]")
            for btn_name, (rel_x, rel_y) in buttons.items():
                pixel_x = self.area.left + int(rel_x * self.area.width)
                pixel_y = self.area.top + int(rel_y * self.area.height)
                print(f"  {btn_name:30s} -> rel({rel_x:.3f}, {rel_y:.3f}) px({pixel_x}, {pixel_y})")

    def test_button(self, screen_name: str, button_name: str) -> None:
        """Testa um botão específico."""
        if screen_name not in self.buttons or button_name not in self.buttons[screen_name]:
            print(f"Botão não encontrado: [{screen_name}] {button_name}")
            return

        rel_x, rel_y = self.buttons[screen_name][button_name]

        print(f"\n{'='*70}")
        print(f"Testando: [{screen_name}] {button_name}")
        print(f"Coordenada relativa: ({rel_x:.3f}, {rel_y:.3f})")
        print(f"{'='*70}")
        print("\nPressione Enter para CLICAR no botão...")
        input()

        try:
            click_relative(rel_x, rel_y, self.area)
            print("✓ Clique executado.")
        except Exception as e:
            print(f"❌ Erro ao clicar: {e}")

        # Perguntar se funcionou e ajustar se necessário
        result = input("\nFuncionou? [S/n/ajustar]: ").strip().lower()
        if result in ("n", "não", "nao"):
            print("Botão não funcionou. Ajuste necessário.")
        elif result == "ajustar":
            self.adjust_button(screen_name, button_name)

    def adjust_button(self, screen_name: str, button_name: str) -> None:
        """Permite ajustar as coordenadas de um botão."""
        print(f"\nAjustando: [{screen_name}] {button_name}")
        print("1. Capturar nova posição do mouse")
        print("2. Digitar coordenadas relativas manualmente")
        print("3. Cancelar")

        choice = input("Escolha [1-3]: ").strip()

        if choice == "1":
            print("Posicione o mouse sobre o botão e pressione Enter...")
            input()
            pixel_x, pixel_y = pyautogui.position()
            rel_x = (pixel_x - self.area.left) / self.area.width
            rel_y = (pixel_y - self.area.top) / self.area.height
            rel_x, rel_y = round(rel_x, 3), round(rel_y, 3)
            print(f"Nova coordenada: ({rel_x:.3f}, {rel_y:.3f})")

        elif choice == "2":
            try:
                rel_x = float(input("Digite rel_x (0.0-1.0): "))
                rel_y = float(input("Digite rel_y (0.0-1.0): "))
                rel_x, rel_y = round(rel_x, 3), round(rel_y, 3)
                print(f"Nova coordenada: ({rel_x:.3f}, {rel_y:.3f})")
            except ValueError:
                print("Valores inválidos.")
                return

        else:
            print("Ajuste cancelado.")
            return

        confirm = input("Confirmar ajuste? [S/n]: ").strip().lower()
        if confirm in ("", "s", "sim"):
            self.buttons[screen_name][button_name] = [rel_x, rel_y]
            self.save_buttons()
            print("✓ Botão ajustado e salvo.")
        else:
            print("Ajuste cancelado.")

    def test_screen_buttons(self, screen_name: str) -> None:
        """Testa todos os botões de uma tela."""
        if screen_name not in self.buttons:
            print(f"Tela não encontrada: {screen_name}")
            return

        buttons = self.buttons[screen_name]
        print(f"\n{'='*70}")
        print(f"Testando todos os botões da tela: {screen_name}")
        print(f"{'='*70}")

        for btn_name in buttons.keys():
            self.test_button(screen_name, btn_name)
            cont = input("\nContinuar para o próximo botão? [S/n]: ").strip().lower()
            if cont in ("n", "não", "nao"):
                break


def main():
    area = load_action_area()
    if area is None:
        print("❌ Área de ação não configurada. Execute ddtank.py primeiro.")
        return

    tester = ButtonTester(area)

    print("\n" + "="*70)
    print("TESTADOR DE BOTÕES - DDTank")
    print("="*70)

    while True:
        print("\nOpções:")
        print("1. Listar todos os botões")
        print("2. Testar um botão específico")
        print("3. Testar todos os botões de uma tela")
        print("4. Sair")

        choice = input("\nEscolha uma opção [1-4]: ").strip()

        if choice == "1":
            tester.list_all_buttons()

        elif choice == "2":
            screen = input("Nome da tela: ").strip()
            button = input("Nome do botão: ").strip()
            tester.test_button(screen, button)

        elif choice == "3":
            screen = input("Nome da tela: ").strip()
            tester.test_screen_buttons(screen)

        elif choice == "4":
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
