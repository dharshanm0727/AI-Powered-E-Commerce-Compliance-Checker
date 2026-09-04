import pytest
from app.services.compliance_engine import ComplianceEngine, run_full_compliance_workflow
from app.models.product import Product
from app.models.report import ComplianceReport, ViolationDetail
from app.models.category import ProductCategory
from app.models.rule import ComplianceRule, RuleCategoryMapping


def test_compliance_engine_violation_classification():
    # 1. PASSED
    v_type, severity = ComplianceEngine._classify_violation("PASSED", "P/N 12345", 0.95, "strict")
    assert v_type == "PASSED"
    assert severity == "none"

    # 2. MISSING
    v_type, severity = ComplianceEngine._classify_violation("FAILED", "Not Found", 0.0, "strict")
    assert v_type == "MISSING"
    assert severity == "critical"

    # 3. AMBIGUOUS (low confidence)
    v_type, severity = ComplianceEngine._classify_violation("PASSED", "Uncertain Value", 0.3, "warning")
    assert v_type == "AMBIGUOUS"
    assert severity == "warning"

    # 4. INCORRECT
    v_type, severity = ComplianceEngine._classify_violation("FAILED", "Wrong Format", 0.8, "strict")
    assert v_type == "INCORRECT"
    assert severity == "critical"


def test_full_compliance_workflow(db, sample_category, sample_rule):
    product = Product(
        title="Smart Electric Kettle 1.5L",
        url="https://www.example.com/kettle-123",
        domain="example.com"
    )
    db.add(product)
    db.commit()

    report = ComplianceReport(
        product_id=product.id,
        category_id=sample_category.id,
        overall_status="PENDING",
        step_reached=1
    )
    db.add(report)
    db.commit()

    # Run workflow
    run_full_compliance_workflow(report.id, db)

    db.refresh(report)
    assert report.step_reached == 10
    assert report.overall_status in ["COMPLIANT", "WARNING", "NON_COMPLIANT", "REVIEW", "INSUFFICIENT_EVIDENCE"]
    assert report.reasoning_summary is not None
    assert len(report.reasoning_summary) > 0


def test_compliance_engine_retrieve_applicable_rules(db, sample_category, sample_rule):
    engine = ComplianceEngine(db)
    rules = engine.retrieve_applicable_rules(sample_category)
    assert len(rules) > 0
    assert any(r.rule_code == sample_rule.rule_code for r in rules)
