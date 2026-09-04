from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class RuleBase(BaseModel):
    """Base compliance rule fields."""
    rule_code: str
    declaration_name: str
    description: Optional[str] = None
    mandatory_fields: str
    enforcement_level: str = "strict"
    rule_type: str = "ONLINE_MANDATORY"  # ONLINE_MANDATORY, ONLINE_CONDITIONAL, PACKAGE_OR_IMAGE_VERIFICATION, PRODUCT_SPECIFIC
    applicability_type: str = "MANDATORY"
    evidence_source: str = "HTML_OR_IMAGE"
    applicability_condition_json: Optional[Dict[str, Any]] = None
    source_name: Optional[str] = None
    regulation_name: Optional[str] = None
    source_reference: Optional[str] = None
    regulation_version: Optional[str] = "2024.1"
    effective_date: Optional[str] = None
    applicability_notes: Optional[str] = None
    verification_status: Optional[str] = "VERIFIED"
    legal_reference: Optional[str] = None
    version: str = "2024.1"


class RuleCreate(RuleBase):
    """Compliance rule creation request."""
    pass


class RuleUpdate(BaseModel):
    """Compliance rule update request."""
    rule_code: Optional[str] = None
    declaration_name: Optional[str] = None
    description: Optional[str] = None
    mandatory_fields: Optional[str] = None
    enforcement_level: Optional[str] = None
    rule_type: Optional[str] = None
    applicability_type: Optional[str] = None
    evidence_source: Optional[str] = None
    applicability_condition_json: Optional[Dict[str, Any]] = None
    source_name: Optional[str] = None
    regulation_name: Optional[str] = None
    source_reference: Optional[str] = None
    regulation_version: Optional[str] = None
    effective_date: Optional[str] = None
    applicability_notes: Optional[str] = None
    verification_status: Optional[str] = None
    legal_reference: Optional[str] = None
    version: Optional[str] = None


class RuleOut(RuleBase):
    """Compliance rule response model."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class RuleCategoryMappingCreate(BaseModel):
    """Rule-category mapping creation request."""
    category_id: int
    rule_id: int
    is_required: bool = True
    notes: Optional[str] = None


class RuleCategoryMappingOut(BaseModel):
    """Rule-category mapping response model."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    rule_id: int
    is_required: bool
    notes: Optional[str] = None
    created_at: datetime
    rule: Optional[RuleOut] = None
    category_name: Optional[str] = None
