"""
Script para testar o fluxo completo de mineração.
Começa com um clique na borda para acordar a janela do jogo.
Depois segue o caminho automaticamente: dd_mineracao > campo_de_mineracao > iniciar_mineracao.
"""

import time
import logging
from pathlib import Path

try:
    from ddtank import ActionArea, click_relative, load_action_area, focus_game_window
    from screen_recognition import ScreenRecognition, ScreenState
    from button_coords_gen import DdMineracao
except Exception:
    import traceback

    print("Erro ao importar módulos necessários:")
    traceback.print_exc()
    input("Pressione Enter para encerrar...")
    raise


class MiningFlowExecutor:
    def __init__(self, area: ActionArea):
        self.area = area
        self.recognition = ScreenRecognition()
        self.max_attempts = 15
        self.attempt_count = 0

    def wake_up_game(self) -> None:
        """Clica no ponto configurado para acordar/ativar a janela do jogo."""
        self.logger.info("[1/4] Acordando a janela do jogo...")
        print("\n[1/4] Acordando a janela do jogo...")
        click_relative(self.area.wake_rel_x, self.area.wake_rel_y, self.area)
        time.sleep(0.2)
        self.logger.info("Janela ativada.")
        print("✓ Janela ativada.")

    def get_current_screen(self) -> ScreenState:
        """Detecta a tela atual."""
        state, confidence = self.recognition.recognize_screen(self.area)
        msg = f"  Tela detectada: {state.value} (confiança: {confidence:.3f})"
        self.logger.info(msg)
        print(msg)
        return state

    def navigate_to_mining(self) -> bool:
        """Navega do estado atual até iniciar_mineracao."""
        self.logger.info("[2/4] Navegando até mineração...")
        print("\n[2/4] Navegando até mineração...")

        while self.attempt_count < self.max_attempts:
            self.attempt_count += 1
            current_state = self.get_current_screen()

            if current_state == ScreenState.DD_MINERACAO:
                self.logger.info("Ação: clicando em 'Iniciar Mineração'")
                print("  Ação: clicando em 'Iniciar Mineração'")
                click_relative(DdMineracao.INICIAR_MINERACAO.rel_x, DdMineracao.INICIAR_MINERACAO.rel_y, self.area)
                time.sleep(3)

            elif current_state == ScreenState.CAMPO_DE_MINERACAO:
                print("✓ Chegou ao Campo de Mineração!")
                return True

            elif current_state == ScreenState.DESCONHECIDO:
                self.logger.warning("Tela desconhecida. Aguardando...")
                print("  ⚠ Tela desconhecida. Aguardando...")
                time.sleep(1)

            else:
                print(f"  ⚠ Tela inesperada: {current_state.value}")
                time.sleep(1)

        print(f"❌ Não conseguiu chegar à mineração após {self.max_attempts} tentativas.")
        return False

    def run(self) -> None:
        """Executa o fluxo completo."""
        print("\n" + "="*70)
        print("TESTE DE FLUXO DE MINERAÇÃO")
        print("="*70)
        self.logger.info("Iniciando teste de fluxo de mineração")

        self.wake_up_game()
        time.sleep(0.2)

        success = self.navigate_to_mining()

        if success:
            print("\n" + "="*70)
            print("✓ FLUXO COMPLETO FUNCIONOU!")
            print("="*70)
            self.print_summary()
        else:
            print("\n" + "="*70)
            print("❌ FLUXO NÃO COMPLETOU")
            print("="*70)
            self.logger.error("Fluxo não completou")

    def print_summary(self) -> None:
        """Exibe resumo do fluxo."""
        print("\nSequência de telas percorridas:")
        print("  1. DD Mineração")
        print("  2. Campo de Mineração")
        print(f"\nTentativas: {self.attempt_count}")


def main():
    area = load_action_area()
    if area is None:
        print("❌ Área de ação não configurada. Execute ddtank.py primeiro.")
        return

    # configurar logger
    log_file = Path(__file__).with_name("mining_flow.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        handlers=[logging.FileHandler(log_file, encoding="utf-8"), logging.StreamHandler()],
    )

    executor = MiningFlowExecutor(area)
    # anexar logger ao executor
    executor.logger = logging.getLogger("mining_flow")

    print("\nAVISO: O script fará cliques automáticos na janela do jogo.")
    input("Pressione Enter para iniciar o fluxo de mineração (ou Ctrl+C para cancelar)...")

    executor.run()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback

        print("\nErro inesperado:")
        traceback.print_exc()
    finally:
        input("\nPressione Enter para encerrar...")
