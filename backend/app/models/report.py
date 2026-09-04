from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Text, Float, Boolean, DateTime, ForeignKey, JSON, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class ComplianceReport(Base):
    __tablename__ = "compliance_reports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("product_categories.id", ondelete="SET NULL"), nullable=True, index=True)
    subcategory_id: Mapped[Optional[int]] = mapped_column(ForeignKey("product_subcategories.id", ondelete="SET NULL"), nullable=True, index=True)
    
    overall_status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False, index=True)  # COMPLIANT, NON_COMPLIANT, WARNING, PENDING, FAILED, REVIEW
    overall_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    step_reached: Mapped[int] = mapped_column(default=1, nullable=False)
    html_checked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ocr_checked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reasoning_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    detected_attributes: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    product: Mapped["Product"] = relationship("Product", back_populates="reports")
    user: Mapped[Optional["User"]] = relationship("User", back_populates="reports")
    category: Mapped[Optional["ProductCategory"]] = relationship("ProductCategory", back_populates="reports")
    subcategory: Mapped[Optional["ProductSubcategory"]] = relationship("ProductSubcategory")
    violations: Mapped[List["ViolationDetail"]] = relationship("ViolationDetail", back_populates="report", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_reports_product_status", "product_id", "overall_status"),
        Index("idx_reports_user_created", "user_id", "created_at"),
    )

class ViolationDetail(Base):
    __tablename__ = "violation_details"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("compliance_reports.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_id: Mapped[int] = mapped_column(ForeignKey("compliance_rules.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # PASSED, FAILED, MISSING, NOT_APPLICABLE, AMBIGUOUS, REVIEW_REQUIRED
    evidence_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True) # FOUND, MISSING_FROM_HTML, FOUND_BY_OCR, NOT_APPLICABLE, INVALID, AMBIGUOUS, INSUFFICIENT_EVIDENCE, REVIEW_REQUIRED
    evidence_source: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # HTML, IMAGE_OCR, PACKAGE_ONLY, MANUAL_REVIEW
    field_name: Mapped[str] = mapped_column(String(255), nullable=False)
    expected_rule: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    actual_found: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    ai_reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    report: Mapped["ComplianceReport"] = relationship("ComplianceReport", back_populates="violations")
    rule: Mapped["ComplianceRule"] = relationship("ComplianceRule", back_populates="violations")

    __table_args__ = (
        Index("idx_violations_report_status", "report_id", "status"),
    )
