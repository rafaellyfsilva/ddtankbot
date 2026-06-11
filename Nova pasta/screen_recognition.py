import cv2
import numpy as np
from dataclasses import dataclass
from pathlib import Path
from enum import Enum

from ddtank import ActionArea, capture_action_area


class ScreenState(Enum):
    DD_MINERACAO = "dd_mineracao"
    CAMPO_DE_MINERACAO = "campo_de_mineracao"
    HOMEM_DE_NEGOCIOS = "homem_de_negocios"
    DESCONHECIDO = "desconhecido"


@dataclass
class ScreenTemplate:
    state: ScreenState
    paths: list[Path]
    templates: list[np.ndarray] = None
    threshold: float = 0.7

    def load(self) -> None:
        self.templates = []
        if not self.paths:
            print(f"Nenhum template definido para: {self.state.value}")
            return

        for path in self.paths:
            if path.exists():
                img = cv2.imread(str(path))
                if img is not None:
                    self.templates.append(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
                    print(f"Template carregado: {path}")
                else:
                    print(f"Erro ao carregar template: {path}")
            else:
                print(f"Arquivo não encontrado: {path}")


class ScreenRecognition:
    def __init__(self, screenshots_dir: Path = None):
        if screenshots_dir is None:
            screenshots_dir = Path(__file__).with_name("screenshots")

        self.screenshots_dir = screenshots_dir
        self.templates = [
            ScreenTemplate(
                ScreenState.DD_MINERACAO,
                self._collect_templates(screenshots_dir, "dd_mineracao"),
                threshold=0.75,
            ),
            ScreenTemplate(
                ScreenState.CAMPO_DE_MINERACAO,
                self._collect_templates(screenshots_dir, "campo_de_mineracao"),
                threshold=0.75,
            ),
            ScreenTemplate(
                ScreenState.HOMEM_DE_NEGOCIOS,
                self._collect_templates(screenshots_dir, "homem_de_negocios"),
                threshold=0.75,
            ),
        ]

        for template in self.templates:
            template.load()

    def _collect_templates(self, screenshots_dir: Path, state_name: str) -> list[Path]:
        state_dir = screenshots_dir / state_name
        if state_dir.exists() and state_dir.is_dir():
            return sorted(state_dir.glob("*.png"))
        return [screenshots_dir / f"{state_name}.png"]

    def _compute_match_confidences(self, current_cv: np.ndarray) -> list[tuple[ScreenState, float]]:
        scores = []
        for template in self.templates:
            if not template.templates:
                scores.append((template.state, 0.0))
                continue

            state_best = 0.0
            for temp in template.templates:
                h, w = temp.shape
                if h > current_cv.shape[0] or w > current_cv.shape[1]:
                    continue

                result = cv2.matchTemplate(current_cv, temp, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(result)
                state_best = max(state_best, float(max_val))

            scores.append((template.state, state_best))

        return sorted(scores, key=lambda item: item[1], reverse=True)

    def recognize_screen(self, area: ActionArea) -> tuple[ScreenState, float]:
        # 1. Captura a imagem utilizando a região exata
        current_screenshot = capture_action_area(area)
        if current_screenshot is None:
            return ScreenState.DESCONHECIDO, 0.0

        # 👉 SALVA O PRINT DE DEPURAÇÃO PARA VERMOS O QUE O BOT ESTÁ VENDO
        caminho_debug = Path(__file__).parent / "debug_print.png"
        current_screenshot.save(caminho_debug)

        # 2. Converte para Tons de Cinza do OpenCV
        current_cv = cv2.cvtColor(np.array(current_screenshot), cv2.COLOR_RGB2GRAY)

        # 3. Faz o cálculo matemático de similaridade
        matches = self._compute_match_confidences(current_cv)
        if not matches:
            return ScreenState.DESCONHECIDO, 0.0

        # Extrai o melhor match
        best_state, best_match_value = matches[0]

        # Regras específicas do seu código

        if best_state == ScreenState.DD_MINERACAO:
            # Tratar dd_mineracao e campo_de_mineracao como equivalentes.
            return ScreenState.CAMPO_DE_MINERACAO, best_match_value

        threshold = next((template.threshold for template in self.templates if template.state == best_state), 0.75)
        if best_match_value >= threshold:
            return best_state, best_match_value

        return ScreenState.DESCONHECIDO, best_match_value

    def recognize_screen_verbose(self, area: ActionArea) -> dict:
        current_screenshot = capture_action_area(area)
        if current_screenshot is None:
            return {"current_state": ScreenState.DESCONHECIDO.value, "confidence": 0.0, "matches": {}}
            
        current_cv = cv2.cvtColor(np.array(current_screenshot), cv2.COLOR_RGB2GRAY)

        results = {}
        best_match_value = 0.0
        best_state = ScreenState.DESCONHECIDO

        for template in self.templates:
            if not template.templates:
                results[template.state.value] = {"match": 0.0, "detected": False}
                continue

            state_best = 0.0
            for temp in template.templates:
                h, w = temp.shape
                if h > current_cv.shape[0] or w > current_cv.shape[1]:
                    continue

                result = cv2.matchTemplate(current_cv, temp, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(result)
                state_best = max(state_best, float(max_val))

            detected = state_best >= template.threshold
            results[template.state.value] = {
                "match": round(state_best, 3),
                "detected": detected,
            }

            if detected and state_best > best_match_value:
                best_match_value = state_best
                best_state = template.state

        return {
            "current_state": best_state.value,
            "confidence": round(best_match_value, 3),
            "matches": results,
        }
    def recognize_screen_verbose(self, area: ActionArea) -> dict:
        current_screenshot = capture_action_area(area)
        current_cv = cv2.cvtColor(np.array(current_screenshot), cv2.COLOR_RGB2GRAY)

        results = {}
        best_match_value = 0.0
        best_state = ScreenState.DESCONHECIDO

        for template in self.templates:
            if not template.templates:
                results[template.state.value] = {"match": 0.0, "detected": False}
                continue

            state_best = 0.0
            for temp in template.templates:
                h, w = temp.shape
                if h > current_cv.shape[0] or w > current_cv.shape[1]:
                    continue

                result = cv2.matchTemplate(current_cv, temp, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(result)
                state_best = max(state_best, float(max_val))

            detected = state_best >= template.threshold
            results[template.state.value] = {
                "match": round(state_best, 3),
                "detected": detected,
            }

            if detected and state_best > best_match_value:
                best_match_value = state_best
                best_state = template.state

        return {
            "current_state": best_state.value,
            "confidence": round(best_match_value, 3),
            "matches": results,
        }


def test_recognition(area: ActionArea) -> None:
    recognition = ScreenRecognition()
    print("Testando reconhecimento de telas...")
    state, confidence = recognition.recognize_screen(area)
    print(f"Estado detectado: {state.value}")
    print(f"Confiança: {confidence:.3f}")

    print("\nDetalhes completos:")
    verbose = recognition.recognize_screen_verbose(area)
    for key, value in verbose["matches"].items():
        print(f"  {key}: {value['match']:.3f} {'✓' if value['detected'] else '✗'}")


if __name__ == "__main__":
    try:
        from ddtank import load_action_area

        area = load_action_area()
        if area is None:
            print("Área de ação não configurada. Execute ddtank.py primeiro.")
        else:
            test_recognition(area)
    except Exception as e:
        import traceback
        print("\nErro inesperado:")
        traceback.print_exc()
    finally:
        input("\nPressione Enter para encerrar...")

