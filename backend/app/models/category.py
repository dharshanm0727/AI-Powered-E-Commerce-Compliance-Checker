from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class ProductCategory(Base):
    __tablename__ = "product_categories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    subcategories: Mapped[List["ProductSubcategory"]] = relationship("ProductSubcategory", back_populates="category", cascade="all, delete-orphan")
    rule_mappings: Mapped[List["RuleCategoryMapping"]] = relationship("RuleCategoryMapping", back_populates="category", cascade="all, delete-orphan")
    reports: Mapped[List["ComplianceReport"]] = relationship("ComplianceReport", back_populates="category")

    __table_args__ = (
        Index("idx_category_name", "name"),
    )

class ProductSubcategory(Base):
    __tablename__ = "product_subcategories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("product_categories.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    category: Mapped["ProductCategory"] = relationship("ProductCategory", back_populates="subcategories")

    __table_args__ = (
        Index("idx_subcategory_cat_name", "category_id", "name"),
    )
