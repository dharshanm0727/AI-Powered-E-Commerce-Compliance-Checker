from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.schemas.product import ProductOut
from app.schemas.category import CategoryOut, SubcategoryOut
from app.schemas.rule import RuleOut


class ViolationOut(BaseModel):
    """Violation detail response model."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    rule_id: int
    status: str
    evidence_status: Optional[str] = None
    evidence_source: Optional[str] = None
    field_name: str
    expected_rule: Optional[str] = None
    actual_found: Optional[str] = None
    confidence: float
    ai_reasoning: Optional[str] = None
    created_at: datetime
    rule: Optional[RuleOut] = None


class ReportOut(BaseModel):
    """Compliance report response model."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    user_id: Optional[int] = None
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    overall_status: str
    overall_score: float
    step_reached: int
    html_checked: bool
    ocr_checked: bool
    reasoning_summary: Optional[str] = None
    detected_attributes: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    product: Optional[ProductOut] = None
    category: Optional[CategoryOut] = None
    subcategory: Optional[SubcategoryOut] = None
    violations: List[ViolationOut] = []


class ReportListOut(BaseModel):
    """Paginated report list response."""
    total: int
    page: int
    page_size: int
    reports: List[ReportOut]


class DashboardStats(BaseModel):
    """Dashboard statistics response model."""
    total_products_scanned: int
    compliant_count: int
    non_compliant_count: int
    warning_count: int
    pending_count: int
    failed_count: int
    compliance_rate: float
    average_score: float
    recent_reports: List[ReportOut]
    category_breakdown: List[Dict[str, Any]]
    daily_scan_counts: List[Dict[str, Any]]


class AuditLogOut(BaseModel):
    """Audit log response model."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime
