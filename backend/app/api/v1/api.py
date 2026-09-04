from fastapi import APIRouter
from app.api.v1 import (
    auth, categories, rules, rule_mappings, products,
    compliance, reports, dashboard, ocr, users
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])
api_router.include_router(rules.router, prefix="/rules", tags=["Compliance Rules"])
api_router.include_router(rule_mappings.router, prefix="/rule-mappings", tags=["Rule Mappings"])
api_router.include_router(products.router, prefix="/products", tags=["Products"])
api_router.include_router(compliance.router, prefix="/compliance", tags=["Compliance Checking"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(ocr.router, prefix="/ocr", tags=["OCR Processing"])
