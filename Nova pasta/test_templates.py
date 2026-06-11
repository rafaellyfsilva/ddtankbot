"""
Script para validar templates e testar fluxo simplificado.
Executa diagnóstico antes de rodar o mining_flow.py
"""

import sys
from pathlib import Path
from screen_recognition import ScreenRecognition, ScreenState
from ddtank import load_action_area, capture_action_area

def check_template_files():
    """Verifica a estrutura de templates."""
    print("\n" + "="*70)
    print("VALIDACAO DE TEMPLATES")
    print("="*70)
    
    screenshots_dir = Path(__file__).with_name("screenshots")
    
    states = [
        ("dd_mineracao", ScreenState.DD_MINERACAO),
        ("campo_de_mineracao", ScreenState.CAMPO_DE_MINERACAO),
        ("homem_de_negocios", ScreenState.HOMEM_DE_NEGOCIOS),
    ]
    
    for dir_name, state in states:
        state_dir = screenshots_dir / dir_name
        print(f"\n[DIR] {state.value}:")
        print(f"  Caminho: {state_dir}")
        print(f"  Existe: {'OK' if state_dir.exists() else 'FAIL'}")
        
        if state_dir.exists():
            templates = sorted(state_dir.glob("*.png"))
            print(f"  Templates encontrados: {len(templates)}")
            for tmpl in templates:
                print(f"    - {tmpl.name}")
        else:
            print(f"  ERRO: Diretorio nao encontrado!")

def test_recognition():
    """Testa o reconhecimento de telas."""
    print("\n" + "="*70)
    print("TESTE DE RECONHECIMENTO")
    print("="*70)
    
    area = load_action_area()
    if area is None:
        print("ERRO: Area de acao nao configurada.")
        print("  Execute ddtank.py primeiro para configurar.")
        return False
    
    print(f"OK: Area de acao carregada: {area.left}, {area.top} ({area.width}x{area.height})")
    
    try:
        recognition = ScreenRecognition()
        print("OK: ScreenRecognition inicializado com sucesso")
        
        # Testar com screenshot
        print("\n[*] Capturando screenshot da tela atual...")
        current_state, confidence = recognition.recognize_screen(area)
        
        print(f"\n[RESULTADO]")
        print(f"  Tela detectada: {current_state.value}")
        print(f"  Confianca: {confidence:.3f}")
        
        if current_state == ScreenState.DESCONHECIDO:
            print("\nAVISO: Tela nao reconhecida!")
            print("  Possiveis razoes:")
            print("  - Templates nao correspondem a tela atual")
            print("  - Threshold de confianca muito alto")
            print("  - Area de acao nao alinhada corretamente")
            
            # Mostrar todas as confiancas
            print("\n[CONFIANCAS POR TELA]")
            verbose_results = recognition.recognize_screen_verbose(area)
            for state_name, match_info in verbose_results.get("matches", {}).items():
                conf = match_info.get("match", 0.0)
                detected = match_info.get("detected", False)
                status = "OK" if detected else "FAIL"
                print(f"  [{status}] {state_name}: {conf:.3f}")
        
        return True
        
    except Exception as e:
        print(f"ERRO ao testar reconhecimento: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "[TESTE DE FLUXO SIMPLIFICADO]".center(70, "="))
    
    check_template_files()
    
    if not test_recognition():
        print("\nAVISO: Falha na validacao de templates.")
        print("  Proximas acoes:")
        print("  1. Verifique se os templates estao nos diretorios corretos")
        print("  2. Compare templates com a tela atual (debug_print.png)")
        print("  3. Ajuste thresholds se necessario")
        return
    
    print("\n" + "="*70)
    print("OK: VALIDACAO CONCLUIDA COM SUCESSO!")
    print("="*70)
    print("\nO fluxo esta pronto para ser testado.")
    print("Execute: python mining_flow.py")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nERRO inesperado: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("\nPressione Enter para encerrar...")
