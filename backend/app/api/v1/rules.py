from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_active_admin
from app.models.rule import ComplianceRule
from app.models.audit import AuditLog
from app.models.user import User
from app.schemas.rule import RuleCreate, RuleUpdate, RuleOut

router = APIRouter()


@router.get(
    "/",
    response_model=List[RuleOut],
    summary="List All Compliance Rules",
    description="Retrieve a list of all compliance rules with optional filters."
)
def list_rules(
    enforcement_level: Optional[str] = Query(None, description="Filter by enforcement level"),
    version: Optional[str] = Query(None, description="Filter by version"),
    search: Optional[str] = Query(None, description="Search term for rule code, declaration name, or description"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(ComplianceRule)
    if enforcement_level:
        query = query.filter(ComplianceRule.enforcement_level == enforcement_level)
    if version:
        query = query.filter(ComplianceRule.version == version)
    if search:
        query = query.filter(
            or_(
                ComplianceRule.rule_code.ilike(f"%{search}%"),
                ComplianceRule.declaration_name.ilike(f"%{search}%"),
                ComplianceRule.description.ilike(f"%{search}%")
            )
        )
    return query.offset(skip).limit(limit).all()


@router.get(
    "/{rule_id}",
    response_model=RuleOut,
    summary="Get Compliance Rule By ID",
    description="Retrieve a specific compliance rule by its ID."
)
def get_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(ComplianceRule).filter(ComplianceRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Compliance rule not found")
    return rule


@router.post(
    "/",
    response_model=RuleOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create Compliance Rule (Admin)",
    description="Create a new compliance rule. Requires admin privileges."
)
def create_rule(
    rule_in: RuleCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    existing = db.query(ComplianceRule).filter(ComplianceRule.rule_code == rule_in.rule_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Compliance rule with this rule_code already exists")

    rule = ComplianceRule(**rule_in.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)

    db.add(AuditLog(action="create_rule", user_id=current_admin.id, entity_type="ComplianceRule", entity_id=rule.id, details={"rule_code": rule.rule_code}))
    db.commit()

    return rule


@router.put(
    "/{rule_id}",
    response_model=RuleOut,
    summary="Update Compliance Rule (Admin)",
    description="Update an existing compliance rule. Requires admin privileges."
)
def update_rule(
    rule_id: int,
    rule_in: RuleUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    rule = db.query(ComplianceRule).filter(ComplianceRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Compliance rule not found")

    update_data = rule_in.model_dump(exclude_unset=True)
    if "rule_code" in update_data:
        existing = db.query(ComplianceRule).filter(ComplianceRule.rule_code == update_data["rule_code"], ComplianceRule.id != rule_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Compliance rule with this rule_code already exists")

    for field, value in update_data.items():
        setattr(rule, field, value)

    db.commit()
    db.refresh(rule)

    db.add(AuditLog(action="update_rule", user_id=current_admin.id, entity_type="ComplianceRule", entity_id=rule.id, details=update_data))
    db.commit()

    return rule


@router.delete(
    "/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Delete Compliance Rule (Admin)",
    description="Delete a compliance rule. Requires admin privileges."
)
def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    rule = db.query(ComplianceRule).filter(ComplianceRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Compliance rule not found")

    rule_code = rule.rule_code
    db.delete(rule)
    db.add(AuditLog(action="delete_rule", user_id=current_admin.id, entity_type="ComplianceRule", entity_id=rule_id, details={"rule_code": rule_code}))
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
