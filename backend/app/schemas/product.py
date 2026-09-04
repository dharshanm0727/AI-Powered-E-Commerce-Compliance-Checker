from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class ProductSubmit(BaseModel):
    """URL submission request for compliance checking."""
    url: str


class DeclarationOut(BaseModel):
    """Extracted declaration response model."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    source: str
    key_name: str
    raw_value: Optional[str] = None
    normalized_value: Optional[str] = None
    confidence_score: float
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime


class OCRDeclarationOut(BaseModel):
    """OCR declaration response model."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    image_url: str
    detected_text: Optional[str] = None
    corrected_text: Optional[str] = None
    bounding_boxes: Optional[List[Dict[str, Any]]] = None
    created_at: datetime


class ProductOut(BaseModel):
    """Product response model."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: Optional[str] = None
    url: str
    domain: Optional[str] = None
    image_urls: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime


class ProductDetailOut(ProductOut):
    """Product response model with declarations."""
    extracted_declarations: List[DeclarationOut] = []
    ocr_declarations: List[OCRDeclarationOut] = []
