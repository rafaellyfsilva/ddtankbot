"""Teste rápido: iniciar e interromper mineração."""

import time
from pathlib import Path

try:
    from ddtank import click_relative, load_action_area
    from button_coords_gen import DdMineracao
except Exception:
    import traceback

    print("Erro ao importar módulos necessários:")
    traceback.print_exc()
    input("Pressione Enter para encerrar...")
    raise


def wake_game(area) -> None:
    """Tenta acordar o jogo clicando no ponto configurado."""
    print("\nAcordando a janela do jogo...")
    click_relative(area.wake_rel_x, area.wake_rel_y, area)
    time.sleep(0.5)
    print("✓ Janela acordada.")


def start_mining(area) -> None:
    """Clica no botão de iniciar mineração."""
    print("\nIniciando mineração...")
    click_relative(DdMineracao.INICIAR_MINERACAO.rel_x, DdMineracao.INICIAR_MINERACAO.rel_y, area)
    time.sleep(1)
    print("✓ Clique em iniciar mineração enviado.")


def main() -> None:
    area = load_action_area()
    if area is None:
        print("❌ Área de ação não configurada. Execute ddtank.py primeiro.")
        return

    print("\nScript de teste rápido de mineração")
    print("Certifique-se de que o jogo esteja aberto e na tela de mineração.")
    input("Pressione Enter para acordar o jogo...")

    wake_game(area)
    input("Pressione Enter para clicar em iniciar mineração...")

    start_mining(area)

    duration = input("Tempo de mineração em segundos [padrão 6]: ").strip()
    if not duration:
        duration = 6
    else:
        duration = int(duration)

    print(f"Aguardando {duration} segundos...")
    time.sleep(duration)

    print("\nAgora você pode ir para a tela do homem de negócios para encerrar a mineração automaticamente.")
    input("Pressione Enter quando estiver pronto para encerrar o teste...")

    print("\nTeste concluído.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Erro inesperado: {exc}")
        import traceback

        traceback.print_exc()
    finally:
        input("\nPressione Enter para encerrar...")
