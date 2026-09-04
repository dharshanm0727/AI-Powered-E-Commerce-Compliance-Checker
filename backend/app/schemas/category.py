from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class SubcategoryOut(BaseModel):
    """Subcategory response model."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class CategoryBase(BaseModel):
    """Base category fields."""
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    """Category creation request."""
    pass


class CategoryUpdate(BaseModel):
    """Category update request."""
    name: Optional[str] = None
    description: Optional[str] = None


class CategoryOut(CategoryBase):
    """Category response model."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    subcategories: List[SubcategoryOut] = []


class CategoryWithRulesOut(CategoryOut):
    """Category response with associated rules."""
    rule_count: int = 0
