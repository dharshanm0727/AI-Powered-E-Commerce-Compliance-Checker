import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

class ImagePreprocessor:
    """
    OpenCV Image Preprocessor for OCR.
    Supports Grayscale conversion, Noise Removal, Skew/Rotation Correction, and Otsu Binarization Thresholding.
    """

    @staticmethod
    def grayscale(img: np.ndarray) -> np.ndarray:
        """Convert BGR image to Grayscale."""
        if len(img.shape) == 3:
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img

    @staticmethod
    def noise_removal(img: np.ndarray) -> np.ndarray:
        """Apply median blur and bilateral filtering to reduce noise."""
        blurred = cv2.medianBlur(img, 3)
        return cv2.bilateralFilter(blurred, 9, 75, 75)

    @staticmethod
    def thresholding(img: np.ndarray) -> np.ndarray:
        """Apply Otsu adaptive binarization thresholding for sharp text edges."""
        _, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh

    @staticmethod
    def rotation_correction(img: np.ndarray) -> np.ndarray:
        """Detect text skew angle and rotate image to correct orientation."""
        try:
            coords = np.column_stack(np.where(img < 255 if np.mean(img) > 127 else img > 0))
            if coords.size == 0:
                return img
            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle

            if abs(angle) > 0.5:
                (h, w) = img.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
                return rotated
            return img
        except Exception:
            return img

    @classmethod
    def preprocess_bytes(cls, image_bytes: bytes) -> bytes:
        """Complete preprocessing pipeline combining grayscale, noise removal, deskew, and thresholding."""
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                return image_bytes

            gray = cls.grayscale(img)
            denoised = cls.noise_removal(gray)
            rotated = cls.rotation_correction(denoised)
            
            # CLAHE contrast enhancement
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(rotated)

            thresh = cls.thresholding(enhanced)

            is_success, buffer = cv2.imencode(".png", thresh)
            if is_success:
                return buffer.tobytes()
            return image_bytes
        except Exception as e:
            logger.error(f"Image preprocessing exception: {e}")
            return image_bytes
