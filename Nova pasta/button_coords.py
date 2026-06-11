"""
Mapeamento de coordenadas dos botões do jogo DDTank.
Coordenadas em valores relativos (0.0 a 1.0) dentro do modal 997x600.

Exemplo:
    rel_x = 0.5  ->  pixel absoluto = 0.5 * 997 = ~498
    rel_y = 0.5  ->  pixel absoluto = 0.5 * 600 = ~300
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class ButtonCoord:
    """Representa um botão com coordenadas relativas."""
    rel_x: float
    rel_y: float
    name: str = ""

    def __str__(self) -> str:
        return f"{self.name or 'Button'} ({self.rel_x:.2f}, {self.rel_y:.2f})"


# ============= TELA: CAMPO_DE_MINERACAO =============
class CampoDeMineracao:
    """Coordenadas da tela de mineração."""
    MINERAR = ButtonCoord(0.5, 0.5, "Minerar")  # AJUSTAR
    DROPAR = ButtonCoord(0.5, 0.7, "Dropar")    # AJUSTAR
    RETORNAR = ButtonCoord(0.1, 0.9, "Retornar") # AJUSTAR


# ============= TELA: HOMEM_DE_NEGOCIOS =============
class HomemDeNegocios:
    """Coordenadas da tela de loja."""
    VENDER = ButtonCoord(0.5, 0.5, "Vender")   # AJUSTAR
    COMPRAR = ButtonCoord(0.5, 0.6, "Comprar") # AJUSTAR
    RETORNAR = ButtonCoord(0.1, 0.9, "Retornar") # AJUSTAR


# ============= CONJUNTO DE TODAS AS COORDENADAS =============
BUTTONS = {
    "campo_de_mineracao": {
        "minerar": CampoDeMineracao.MINERAR,
        "dropar": CampoDeMineracao.DROPAR,
        "retornar": CampoDeMineracao.RETORNAR,
    },
    "homem_de_negocios": {
        "vender": HomemDeNegocios.VENDER,
        "comprar": HomemDeNegocios.COMPRAR,
        "retornar": HomemDeNegocios.RETORNAR,
    },
}


def print_all_buttons() -> None:
    """Exibe todos os botões mapeados."""
    for screen, buttons in BUTTONS.items():
        print(f"\n[{screen.upper()}]")
        for btn_name, btn_coord in buttons.items():
            print(f"  {btn_name:20s} -> {btn_coord}")


if __name__ == "__main__":
    print("Mapeamento de coordenadas dos botões (Limpo):")
    print_all_buttons()