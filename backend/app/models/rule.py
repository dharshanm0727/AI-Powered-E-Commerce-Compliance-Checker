from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class ComplianceRule(Base):
    __tablename__ = "compliance_rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_code = Column(String(50), unique=True, nullable=False, index=True)
    declaration_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    mandatory_fields = Column(Text, nullable=False)  # Comma-separated alternative key names
    enforcement_level = Column(String(20), default="strict")  # strict, warning, info
    
    # E-Commerce Listing-First Classification (Section 53)
    # ONLINE_MANDATORY, ONLINE_CONDITIONAL, PACKAGE_OR_IMAGE_VERIFICATION, PRODUCT_SPECIFIC, NOT_APPLICABLE
    rule_type = Column(String(50), default="ONLINE_MANDATORY", nullable=False)

    # Dynamic Applicability & Evidence Tracking
    applicability_type = Column(String(20), default="MANDATORY")  # MANDATORY, CONDITIONAL
    evidence_source = Column(String(30), default="HTML_OR_IMAGE")  # HTML, IMAGE_OCR, HTML_OR_IMAGE, PACKAGE_ONLY
    applicability_condition_json = Column(JSON, nullable=True)

    # Regulatory Source Metadata
    source_name = Column(String(200), nullable=True)
    regulation_name = Column(String(200), nullable=True)
    source_reference = Column(String(200), nullable=True)
    regulation_version = Column(String(50), default="2024.1")
    effective_date = Column(String(50), nullable=True)
    applicability_notes = Column(Text, nullable=True)
    verification_status = Column(String(50), default="VERIFIED")

    legal_reference = Column(Text, nullable=True)
    version = Column(String(20), default="2024.1")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category_mappings = relationship("RuleCategoryMapping", back_populates="rule", cascade="all, delete-orphan")
    violations = relationship("ViolationDetail", back_populates="rule")


class RuleCategoryMapping(Base):
    __tablename__ = "rule_category_mappings"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("product_categories.id", ondelete="CASCADE"), nullable=False)
    rule_id = Column(Integer, ForeignKey("compliance_rules.id", ondelete="CASCADE"), nullable=False)
    is_required = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    category = relationship("ProductCategory", back_populates="rule_mappings")
    rule = relationship("ComplianceRule", back_populates="category_mappings")
