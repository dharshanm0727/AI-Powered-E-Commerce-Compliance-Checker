from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_active_admin
from app.models.category import ProductCategory
from app.models.rule import ComplianceRule, RuleCategoryMapping
from app.models.audit import AuditLog
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryOut, CategoryWithRulesOut
from app.schemas.rule import RuleOut

router = APIRouter()


@router.get(
    "/",
    response_model=List[CategoryOut],
    summary="List All Product Categories",
    description="Retrieve a list of all product categories with optional search filtering."
)
def list_categories(
    search: Optional[str] = Query(None, description="Search term for category name or description"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(ProductCategory)
    if search:
        query = query.filter(
            or_(
                ProductCategory.name.ilike(f"%{search}%"),
                ProductCategory.description.ilike(f"%{search}%")
            )
        )
    return query.offset(skip).limit(limit).all()


@router.get(
    "/{category_id}",
    response_model=CategoryWithRulesOut,
    summary="Get Category By ID",
    description="Retrieve a specific product category by its ID, including the count of associated rules."
)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(ProductCategory).filter(ProductCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    rule_count = db.query(RuleCategoryMapping).filter(RuleCategoryMapping.category_id == category_id).count()
    return CategoryWithRulesOut.model_validate({**category.__dict__, "rule_count": rule_count})


@router.post(
    "/",
    response_model=CategoryOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create Product Category (Admin)",
    description="Create a new product category. Requires admin privileges."
)
def create_category(
    category_in: CategoryCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    existing = db.query(ProductCategory).filter(ProductCategory.name == category_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category with this name already exists")

    category = ProductCategory(**category_in.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)

    db.add(AuditLog(action="create_category", user_id=current_admin.id, entity_type="ProductCategory", entity_id=category.id, details={"name": category.name}))
    db.commit()

    return category


@router.put(
    "/{category_id}",
    response_model=CategoryOut,
    summary="Update Product Category (Admin)",
    description="Update an existing product category. Requires admin privileges."
)
def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    category = db.query(ProductCategory).filter(ProductCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    update_data = category_in.model_dump(exclude_unset=True)
    if "name" in update_data:
        existing = db.query(ProductCategory).filter(ProductCategory.name == update_data["name"], ProductCategory.id != category_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Category with this name already exists")

    for field, value in update_data.items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)

    db.add(AuditLog(action="update_category", user_id=current_admin.id, entity_type="ProductCategory", entity_id=category.id, details=update_data))
    db.commit()

    return category


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Delete Product Category (Admin)",
    description="Delete a product category. Requires admin privileges."
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    category = db.query(ProductCategory).filter(ProductCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    cat_name = category.name
    db.delete(category)
    db.add(AuditLog(action="delete_category", user_id=current_admin.id, entity_type="ProductCategory", entity_id=category_id, details={"name": cat_name}))
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{category_id}/rules",
    response_model=List[RuleOut],
    summary="Get Rules For Category",
    description="Retrieve all compliance rules mapped to a specific product category."
)
def get_category_rules(category_id: int, db: Session = Depends(get_db)):
    category = db.query(ProductCategory).filter(ProductCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    rules = db.query(ComplianceRule).join(RuleCategoryMapping).filter(RuleCategoryMapping.category_id == category_id).all()
    return rules
