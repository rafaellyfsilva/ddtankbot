import cv2
import numpy as np
from PIL import Image
from pathlib import Path

def convert_pil_to_cv2(screenshot_pil: Image.Image) -> np.ndarray:
    """
    Converte uma captura de tela do PyAutoGUI (PIL) para o formato do OpenCV (Grayscale).
    Isso otimiza absurdamente a velocidade da busca.
    """
    screen_np = np.array(screenshot_pil)
    # Converte RGB (PIL) para BGR (OpenCV)
    screen_bgr = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
    # Converte BGR para Grayscale (Tons de cinza)
    return cv2.cvtColor(screen_bgr, cv2.COLOR_BGR2GRAY)

def load_template(template_path: Path | str) -> np.ndarray | None:
    """
    Carrega uma imagem do disco diretamente em Tons de Cinza.
    Ideal para carregar na inicialização do bot e guardar na memória.
    """
    template = cv2.imread(str(template_path), cv2.IMREAD_GRAYSCALE)
    if template is None:
        print(f"[AVISO] Não foi possível carregar a imagem: {template_path}")
        return None
    return preprocess_gray(template)


def preprocess_gray(image: np.ndarray) -> np.ndarray:
    """Aplica processamento básico ao grayscale para tornar o matching mais robusto."""
    if image is None:
        return image
    blurred = cv2.GaussianBlur(image, (3, 3), 0)
    return cv2.equalizeHist(blurred)


def match_template_score(screen_gray: np.ndarray, template: np.ndarray) -> float:
    """Retorna o maior score de correspondência entre o crop e o template."""
    if template is None or screen_gray is None:
        return 0.0

    template_h, template_w = template.shape
    screen_h, screen_w = screen_gray.shape
    if screen_h < template_h or screen_w < template_w:
        return 0.0

    result = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)
    return float(max_val)


def match_template(screen_gray: np.ndarray, template: np.ndarray, threshold: float = 0.85) -> tuple[int, int, float] | None:
    """
    Cruza a tela atual com o template (ambos em Tons de Cinza).
    Retorna (Centro_X, Centro_Y, Confiança) se encontrar acima do threshold, senão None.
    """
    if template is None or screen_gray is None:
        return None

    template_h, template_w = template.shape
    screen_h, screen_w = screen_gray.shape

    if screen_h < template_h or screen_w < template_w:
        return None

    # Executa a busca (TM_CCOEFF_NORMED é excelente para lidar com brilho e contraste)
    result = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)

    # Extrai os valores máximos e mínimos e suas localizações
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        center_x = max_loc[0] + (template_w // 2)
        center_y = max_loc[1] + (template_h // 2)
        return (center_x, center_y, max_val)

    return None


# --------------- Funções para matching em CORES (BGR) ---------------

def convert_pil_to_cv2_color(screenshot_pil: Image.Image) -> np.ndarray:
    """Converte PIL para BGR (OpenCV) mantendo informação de cor."""
    screen_np = np.array(screenshot_pil)
    return cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)


def load_template_color(template_path: Path | str) -> np.ndarray | None:
    """Carrega template em cores (BGR) com blur leve."""
    template = cv2.imread(str(template_path), cv2.IMREAD_COLOR)
    if template is None:
        print(f"[AVISO] Não foi possível carregar a imagem: {template_path}")
        return None
    return cv2.GaussianBlur(template, (3, 3), 0)


def preprocess_color(image: np.ndarray) -> np.ndarray:
    """Aplica blur leve mantendo informação de cor."""
    if image is None:
        return image
    return cv2.GaussianBlur(image, (3, 3), 0)


def match_template_score_color(screen_bgr: np.ndarray, template_bgr: np.ndarray) -> float:
    """Template matching em cores (BGR). Preserva diferenças de cor entre gemas."""
    if template_bgr is None or screen_bgr is None:
        return 0.0

    template_h, template_w = template_bgr.shape[:2]
    screen_h, screen_w = screen_bgr.shape[:2]
    if screen_h < template_h or screen_w < template_w:
        return 0.0

    result = cv2.matchTemplate(screen_bgr, template_bgr, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)
    return float(max_val)