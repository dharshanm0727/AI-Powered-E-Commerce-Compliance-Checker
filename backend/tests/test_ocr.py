import pytest
import numpy as np
import cv2
from app.services.ocr.preprocessor import ImagePreprocessor
from app.services.ocr.engine import OCREngineService


def test_ocr_engine_initialization():
    engine = OCREngineService()
    assert engine is not None


def test_image_preprocessor_grayscale_and_noise():
    # Synthetic BGR image
    img = np.ones((200, 200, 3), dtype=np.uint8) * 255
    cv2.putText(img, "MRP Rs. 500", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    gray = ImagePreprocessor.grayscale(img)
    assert len(gray.shape) == 2

    denoised = ImagePreprocessor.noise_removal(gray)
    assert denoised is not None

    thresh = ImagePreprocessor.thresholding(gray)
    assert thresh is not None


def test_image_preprocessor_bytes():
    img = np.ones((100, 200, 3), dtype=np.uint8) * 255
    cv2.putText(img, "NET QTY 500g", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    _, buffer = cv2.imencode(".png", img)
    img_bytes = buffer.tobytes()

    processed_bytes = ImagePreprocessor.preprocess_bytes(img_bytes)
    assert isinstance(processed_bytes, bytes)
    assert len(processed_bytes) > 0


def test_ocr_process_invalid_image_url():
    engine = OCREngineService()
    res = engine.process_image_url("https://invalid.url.test/nonexistent.jpg")
    assert res is not None
    assert "detected_text" in res
    assert res["detected_text"] == ""
