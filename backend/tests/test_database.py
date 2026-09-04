import pytest
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.models.category import ProductCategory
from app.models.rule import ComplianceRule, RuleCategoryMapping
from app.models.product import Product, ExtractedDeclaration, OCRDeclaration
from app.models.report import ComplianceReport, ViolationDetail
from app.models.audit import AuditLog


def test_user_model(db):
    user = User(
        email="testdb@example.com",
        hashed_password="hashed_secret",
        full_name="DB Test User",
        role="user"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    assert user.id is not None
    assert user.email == "testdb@example.com"
    assert user.is_active is True


def test_user_unique_email_constraint(db):
    user1 = User(email="duplicate@example.com", hashed_password="pw1")
    db.add(user1)
    db.commit()

    user2 = User(email="duplicate@example.com", hashed_password="pw2")
    db.add(user2)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_product_category_relationship(db):
    cat = ProductCategory(name="Food & Beverages", description="Packaged food products")
    db.add(cat)
    db.commit()

    rule = ComplianceRule(
        rule_code="LM-FOOD-01",
        declaration_name="Best Before Date",
        mandatory_fields="Best Before, Expiry Date, Use By",
        enforcement_level="strict"
    )
    db.add(rule)
    db.commit()

    mapping = RuleCategoryMapping(category_id=cat.id, rule_id=rule.id)
    db.add(mapping)
    db.commit()

    saved_cat = db.query(ProductCategory).filter(ProductCategory.id == cat.id).first()
    assert len(saved_cat.rule_mappings) == 1
    assert saved_cat.rule_mappings[0].rule.rule_code == "LM-FOOD-01"


def test_product_cascade_deletion(db):
    product = Product(url="https://example.com/item1", title="Test Item")
    db.add(product)
    db.commit()

    decl = ExtractedDeclaration(
        product_id=product.id,
        source="html",
        key_name="MRP",
        raw_value="Rs. 999",
        confidence_score=0.95
    )
    db.add(decl)

    ocr_decl = OCRDeclaration(
        product_id=product.id,
        image_url="https://example.com/img.jpg",
        detected_text="Net Wt 500g"
    )
    db.add(ocr_decl)
    db.commit()

    # Delete product and verify cascade to declarations
    db.delete(product)
    db.commit()

    assert db.query(ExtractedDeclaration).filter(ExtractedDeclaration.product_id == product.id).count() == 0
    assert db.query(OCRDeclaration).filter(OCRDeclaration.product_id == product.id).count() == 0


def test_report_violation_relationship(db):
    product = Product(url="https://example.com/item2", title="Test Item 2")
    db.add(product)
    db.commit()

    rule = ComplianceRule(
        rule_code="LM-CORE-01",
        declaration_name="MRP",
        mandatory_fields="MRP, Maximum Retail Price",
        enforcement_level="strict"
    )
    db.add(rule)
    db.commit()

    report = ComplianceReport(
        product_id=product.id,
        overall_status="NON_COMPLIANT",
        overall_score=50.0
    )
    db.add(report)
    db.commit()

    violation = ViolationDetail(
        report_id=report.id,
        rule_id=rule.id,
        status="MISSING",
        field_name="MRP",
        actual_found="Not Found",
        confidence=1.0,
        ai_reasoning="MRP missing from product page"
    )
    db.add(violation)
    db.commit()

    saved_report = db.query(ComplianceReport).filter(ComplianceReport.id == report.id).first()
    assert len(saved_report.violations) == 1
    assert saved_report.violations[0].status == "MISSING"


def test_audit_log_model(db, test_user):
    log = AuditLog(
        user_id=test_user.id,
        action="TEST_ACTION",
        entity_type="TestEntity",
        entity_id=100,
        details={"info": "success"}
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    assert log.id is not None
    assert log.user_id == test_user.id
    assert log.action == "TEST_ACTION"
