"""
Script para diagnosticar e corrigir estrutura de templates.
"""

import shutil
from pathlib import Path
import cv2
import numpy as np

def analyze_template_files():
    """Analisa e compara templates para identificar qual é qual."""
    screenshots_dir = Path(__file__).with_name("screenshots")
    
    # Caminhos dos templates
    dd_mineracao_tmpl = screenshots_dir / "dd_mineracao" / "dd_mineracao.png"
    campo_tmpl = screenshots_dir / "campo_de_mineracao" / "dd_mineracao.png"
    homem_negocios_tmpl = screenshots_dir / "homem_de_negocios" / "campo_de_mineracao.png"
    
    # Carregar imagens
    templates = {
        "dd_mineracao/dd_mineracao.png": dd_mineracao_tmpl,
        "campo_de_mineracao/dd_mineracao.png": campo_tmpl,
        "homem_de_negocios/campo_de_mineracao.png": homem_negocios_tmpl,
    }
    
    print("\n" + "="*70)
    print("DIAGNÓSTICO DE TEMPLATES")
    print("="*70)
    
    for name, path in templates.items():
        if path.exists():
            img = cv2.imread(str(path))
            if img is not None:
                h, w = img.shape[:2]
                # Calcular hash simples para comparar
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
                print(f"\n📄 {name}")
                print(f"   Tamanho: {w}x{h}")
                print(f"   Caminho: {path}")
                
                # Mostrar alguns pixel values para ajudar na identificação
                center_px = gray[h//2, w//2]
                print(f"   Pixel central (cinza): {center_px}")
            else:
                print(f"\n⚠ Erro ao carregar: {name}")
        else:
            print(f"\n❌ Arquivo não existe: {name}")

def suggest_fixes():
    """Sugere renomeação de arquivos."""
    print("\n" + "="*70)
    print("SUGESTÕES DE CORREÇÃO")
    print("="*70)
    
    screenshots_dir = Path(__file__).with_name("screenshots")
    
    print("\nBasado nos nomes de diretório, os arquivos devem ser renomeados:")
    print("\n1. campo_de_mineracao/dd_mineracao.png")
    print("   → campo_de_mineracao/campo_de_mineracao.png")
    print("\n2. homem_de_negocios/campo_de_mineracao.png")
    print("   → homem_de_negocios/homem_de_negocios.png")
    
    print("\nPara fazer isso automaticamente, você pode:")
    print("\n# No PowerShell:")
    print("cd 'screenshots'")
    print("Move-Item 'campo_de_mineracao/dd_mineracao.png' 'campo_de_mineracao/campo_de_mineracao.png'")
    print("Move-Item 'homem_de_negocios/campo_de_mineracao.png' 'homem_de_negocios/homem_de_negocios.png'")
    
    # Oferecer execução automática
    response = input("\nDeseja renomear os arquivos automaticamente? [S/n]: ").strip().lower()
    if response in ("", "s", "sim"):
        fix_templates()

def fix_templates():
    """Executa a correção de nomes de arquivos."""
    screenshots_dir = Path(__file__).with_name("screenshots")
    
    fixes = [
        (screenshots_dir / "campo_de_mineracao" / "dd_mineracao.png",
         screenshots_dir / "campo_de_mineracao" / "campo_de_mineracao.png"),
        (screenshots_dir / "homem_de_negocios" / "campo_de_mineracao.png",
         screenshots_dir / "homem_de_negocios" / "homem_de_negocios.png"),
    ]
    
    print("\n" + "="*70)
    print("EXECUTANDO CORREÇÕES")
    print("="*70 + "\n")
    
    for src, dest in fixes:
        if src.exists():
            try:
                shutil.move(str(src), str(dest))
                print(f"✓ {src.name} → {dest.name}")
            except Exception as e:
                print(f"❌ Erro ao mover {src.name}: {e}")
        else:
            print(f"⚠ Arquivo não encontrado: {src}")
    
    print("\n✅ Correção concluída!")

if __name__ == "__main__":
    try:
        analyze_template_files()
        suggest_fixes()
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("\nPressione Enter para encerrar...")
