from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.product import Product
from app.models.report import ComplianceReport, ViolationDetail
from app.models.audit import AuditLog
from app.models.user import User
from app.services.compliance_engine import run_full_compliance_workflow
from app.schemas.product import ProductSubmit
from app.schemas.report import ReportOut

router = APIRouter()


@router.post("/check", response_model=ReportOut, summary="Submit URL For Compliance Check")
def submit_compliance_check(
    data: ProductSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Submit a URL for compliance checking.
    """
    product = db.query(Product).filter(Product.url == data.url).first()
    if not product:
        product = Product(url=data.url)
        db.add(product)
        db.flush()

    report = ComplianceReport(product_id=product.id, overall_status='PENDING', user_id=current_user.id)
    db.add(report)
    db.commit()
    db.refresh(report)

    run_full_compliance_workflow(report.id, db)

    report = db.query(ComplianceReport).options(
        joinedload(ComplianceReport.product),
        joinedload(ComplianceReport.category),
        joinedload(ComplianceReport.violations)
    ).filter(ComplianceReport.id == report.id).first()

    audit_log = AuditLog(
        user_id=current_user.id,
        action="compliance_check",
        entity_type="ComplianceReport",
        entity_id=report.id,
        details={"url": data.url}
    )
    db.add(audit_log)
    db.commit()

    return report


@router.post("/recheck/{report_id}", response_model=ReportOut, summary="Re-Run Compliance Check")
def recheck_compliance(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Re-run compliance check on an existing report.
    """
    report = db.query(ComplianceReport).filter(ComplianceReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    report.overall_status = 'PENDING'
    report.overall_score = 0.0
    db.query(ViolationDetail).filter(ViolationDetail.report_id == report.id).delete()
    db.commit()

    run_full_compliance_workflow(report.id, db)

    report = db.query(ComplianceReport).options(
        joinedload(ComplianceReport.product),
        joinedload(ComplianceReport.category),
        joinedload(ComplianceReport.violations)
    ).filter(ComplianceReport.id == report.id).first()

    return report


@router.get("/status/{report_id}", summary="Get Compliance Check Status")
def get_compliance_status(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get the real-time status of a compliance check.
    """
    report = db.query(ComplianceReport).filter(ComplianceReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    return {
        "step_reached": getattr(report, "step_reached", 1),
        "overall_status": report.overall_status,
        "overall_score": report.overall_score,
        "reasoning_summary": report.reasoning_summary
    }
