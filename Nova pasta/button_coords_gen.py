"""
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


# ============= TELA: DD_MINERACAO =============
class DdMineracao:
    """Coordenadas da tela dd_mineracao."""
    INICIAR_MINERACAO = ButtonCoord(0.346, 0.632, "iniciar_mineracao")
    TERMINAR_MINERACAO = ButtonCoord(0.494, 0.842, "terminar_mineracao")
    MOCHILA_RIGHT = ButtonCoord(0.853, 0.834, "mochila_right")
    MOCHILA_LEFT = ButtonCoord(0.758, 0.834, "mochila_left")
    HOMEM_DE_NEGOCIOS = ButtonCoord(0.477, 0.216, "homem_de_negocios")


# ============= TELA: HOMEM_DE_NEGOCIOS =============
class HomemDeNegocios:
    """Coordenadas da tela homem_de_negocios."""
    MOCHILA_RIGHT = ButtonCoord(0.853, 0.839, "mochila_right")
    MOCHILA_LEFT = ButtonCoord(0.757, 0.841, "mochila_left")
    VENDA_MINERIO_SLOT_1 = ButtonCoord(0.195, 0.668, "venda_minerio_slot_1")
    VENDA_MINERIO_SLOT_3 = ButtonCoord(0.347, 0.662, "venda_minerio_slot_3")
    VENDA_MINERIO_SLOT_4 = ButtonCoord(0.419, 0.662, "venda_minerio_slot_4")
    BOTAO_CONFIRMAR_VENDA = ButtonCoord(0.51, 0.683, "botao_confirmar_venda")
    BOTAO_DEFINIR_QUANTIDADE_VENDA = ButtonCoord(0.532, 0.499, "botao_definir_quantidade_venda")
    FECHAR_VENDA = ButtonCoord(0.677, 0.396, "fechar_venda")
    COMPRAR_ITEM_SLOT_1 = ButtonCoord(0.195, 0.877, "comprar_item_slot_1")
    COMPRAR_ITEM_SLOT_2 = ButtonCoord(0.27, 0.879, "comprar_item_slot_2")
    COMPRAR_ITEM_SLOT_3 = ButtonCoord(0.341, 0.876, "comprar_item_slot_3")
    COMPRAR_ITEM_SLOT_4 = ButtonCoord(0.422, 0.874, "comprar_item_slot_4")
    POPUP_CONFIRMAR_COMPRA = ButtonCoord(0.51, 0.678, "popup_confirmar_compra")
    POPUP_DEFINIR_QUANTIDADE_COMPRA_ITEM = ButtonCoord(0.535, 0.501, "popup_definir_quantidade_compra_item")
    POPUP_FECHAR_COMPRA_ITEM = ButtonCoord(0.671, 0.398, "popup_fechar_compra_item")


# ============= TELA: HOMME_DE_NEGOCIOS =============
class HommeDeNegocios:
    """Coordenadas da tela homme_de_negocios."""
    VENDA_MINERIO_SLOT_2 = ButtonCoord(0.268, 0.663, "venda_minerio_slot_2")


# ============= CONJUNTO DE TODAS AS COORDENADAS =============
BUTTONS = {
    "dd_mineracao": {
        "iniciar_mineracao": DdMineracao.INICIAR_MINERACAO,
        "terminar_mineracao": DdMineracao.TERMINAR_MINERACAO,
        "mochila_right": DdMineracao.MOCHILA_RIGHT,
        "mochila_left": DdMineracao.MOCHILA_LEFT,
        "homem_de_negocios": DdMineracao.HOMEM_DE_NEGOCIOS,
    },
    "homem_de_negocios": {
        "mochila_right": HomemDeNegocios.MOCHILA_RIGHT,
        "mochila_left": HomemDeNegocios.MOCHILA_LEFT,
        "venda_minerio_slot_1": HomemDeNegocios.VENDA_MINERIO_SLOT_1,
        "venda_minerio_slot_3": HomemDeNegocios.VENDA_MINERIO_SLOT_3,
        "venda_minerio_slot_4": HomemDeNegocios.VENDA_MINERIO_SLOT_4,
        "botao_confirmar_venda": HomemDeNegocios.BOTAO_CONFIRMAR_VENDA,
        "botao_definir_quantidade_venda": HomemDeNegocios.BOTAO_DEFINIR_QUANTIDADE_VENDA,
        "fechar_venda": HomemDeNegocios.FECHAR_VENDA,
        "comprar_item_slot_1": HomemDeNegocios.COMPRAR_ITEM_SLOT_1,
        "comprar_item_slot_2": HomemDeNegocios.COMPRAR_ITEM_SLOT_2,
        "comprar_item_slot_3": HomemDeNegocios.COMPRAR_ITEM_SLOT_3,
        "comprar_item_slot_4": HomemDeNegocios.COMPRAR_ITEM_SLOT_4,
        "popup_confirmar_compra": HomemDeNegocios.POPUP_CONFIRMAR_COMPRA,
        "popup_definir_quantidade_compra_item": HomemDeNegocios.POPUP_DEFINIR_QUANTIDADE_COMPRA_ITEM,
        "popup_fechar_compra_item": HomemDeNegocios.POPUP_FECHAR_COMPRA_ITEM,
    },
    "homme_de_negocios": {
        "venda_minerio_slot_2": HommeDeNegocios.VENDA_MINERIO_SLOT_2,
    },
}
