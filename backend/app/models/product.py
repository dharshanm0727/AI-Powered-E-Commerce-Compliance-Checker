from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Text, Float, DateTime, ForeignKey, JSON, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, index=True)
    url: Mapped[str] = mapped_column(Text, unique=True, index=True, nullable=False)
    domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    raw_html_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_urls: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    extracted_declarations: Mapped[List["ExtractedDeclaration"]] = relationship("ExtractedDeclaration", back_populates="product", cascade="all, delete-orphan")
    ocr_declarations: Mapped[List["OCRDeclaration"]] = relationship("OCRDeclaration", back_populates="product", cascade="all, delete-orphan")
    reports: Mapped[List["ComplianceReport"]] = relationship("ComplianceReport", back_populates="product")

    __table_args__ = (
        Index("idx_product_domain_url", "domain", "url"),
    )

class ExtractedDeclaration(Base):
    __tablename__ = "extracted_declarations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # "html" or "ocr"
    key_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    raw_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    normalized_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    product: Mapped["Product"] = relationship("Product", back_populates="extracted_declarations")

    __table_args__ = (
        Index("idx_declaration_product_source", "product_id", "source", "key_name"),
    )

class OCRDeclaration(Base):
    __tablename__ = "ocr_declarations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    image_url: Mapped[str] = mapped_column(Text, nullable=False)
    detected_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    corrected_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    bounding_boxes: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    product: Mapped["Product"] = relationship("Product", back_populates="ocr_declarations")

    __table_args__ = (
        Index("idx_ocr_product_image", "product_id", "image_url"),
    )
