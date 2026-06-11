"""Salva crops dos slots especificados para diagnóstico de template matching.
Uso:
    python debug_save_crops.py
Salva imagens em ./screenshots/debug_crops/page_<n>_slot_<i>.png
"""
from pathlib import Path
import time

import cv2
import numpy as np

from ddtank import load_action_area, capture_action_area
import backpack_flow
from vision import convert_pil_to_cv2

OUT_DIR = Path(__file__).with_name("screenshots") / "debug_crops"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SLOTS_TO_INSPECT = [1, 2, 14, 16]


def save_crops():
    area = load_action_area()
    if area is None:
        print("Área de ação não configurada. Execute ddtank.py primeiro.")
        return

    slot_regions = backpack_flow.get_backpack_slot_regions(area)

    for page in range(1, 5):
        print(f"Capturando página {page}...")
        screenshot_pil = capture_action_area(area)
        if screenshot_pil is None:
            print("Falha ao capturar a tela.")
            return
        screen_gray = convert_pil_to_cv2(screenshot_pil)

        for idx in SLOTS_TO_INSPECT:
            if idx - 1 >= len(slot_regions):
                print(f"Slot {idx} não existe na lista de regiões.")
                continue
            slot = slot_regions[idx - 1]
            crop = backpack_flow.crop_slot(screen_gray, area, slot)
            fname = OUT_DIR / f"page_{page}_slot_{idx}.png"
            # Se crop vazio, cria uma imagem branca para referência
            if crop.size == 0:
                empty = 255 * np.ones((60, 60), dtype=np.uint8)
                cv2.imwrite(str(fname), empty)
            else:
                cv2.imwrite(str(fname), crop)
            print(f"  Salvo {fname} (shape={crop.shape})")

        if page < 4:
            backpack_flow.page_right(area)
            time.sleep(0.5)


if __name__ == '__main__':
    save_crops()
