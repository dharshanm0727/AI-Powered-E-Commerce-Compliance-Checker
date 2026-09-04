from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_active_admin
from app.models.category import ProductCategory
from app.models.rule import ComplianceRule, RuleCategoryMapping
from app.models.audit import AuditLog
from app.models.user import User
from app.schemas.rule import RuleCategoryMappingCreate, RuleCategoryMappingOut

router = APIRouter()


@router.get(
    "/",
    response_model=List[RuleCategoryMappingOut],
    summary="List Rule-Category Mappings",
    description="List all rule-category mappings with optional filter by category_id or rule_id."
)
def list_rule_mappings(
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    rule_id: Optional[int] = Query(None, description="Filter by rule ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(RuleCategoryMapping)
    if category_id:
        query = query.filter(RuleCategoryMapping.category_id == category_id)
    if rule_id:
        query = query.filter(RuleCategoryMapping.rule_id == rule_id)

    return query.offset(skip).limit(limit).all()


@router.post(
    "/",
    response_model=RuleCategoryMappingOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create Rule-Category Mapping (Admin)",
    description="Create a new mapping between a category and a rule. Requires admin privileges."
)
def create_rule_mapping(
    mapping_in: RuleCategoryMappingCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    category = db.query(ProductCategory).filter(ProductCategory.id == mapping_in.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    rule = db.query(ComplianceRule).filter(ComplianceRule.id == mapping_in.rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Compliance rule not found")

    existing = db.query(RuleCategoryMapping).filter(
        RuleCategoryMapping.category_id == mapping_in.category_id,
        RuleCategoryMapping.rule_id == mapping_in.rule_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Mapping between this category and rule already exists")

    mapping = RuleCategoryMapping(**mapping_in.model_dump())
    db.add(mapping)
    db.commit()
    db.refresh(mapping)

    db.add(AuditLog(
        action="create_rule_mapping",
        user_id=current_admin.id,
        entity_type="RuleCategoryMapping",
        entity_id=mapping.id,
        details={"category_id": mapping.category_id, "rule_id": mapping.rule_id}
    ))
    db.commit()

    return mapping


@router.delete(
    "/{mapping_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Delete Rule-Category Mapping (Admin)",
    description="Delete a rule-category mapping. Requires admin privileges."
)
def delete_rule_mapping(
    mapping_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    mapping = db.query(RuleCategoryMapping).filter(RuleCategoryMapping.id == mapping_id).first()
    if not mapping:
        raise HTTPException(status_code=404, detail="Rule-category mapping not found")

    cat_id, rule_id = mapping.category_id, mapping.rule_id
    db.delete(mapping)
    db.add(AuditLog(
        action="delete_rule_mapping",
        user_id=current_admin.id,
        entity_type="RuleCategoryMapping",
        entity_id=mapping_id,
        details={"category_id": cat_id, "rule_id": rule_id}
    ))
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
