import pytest
import time
from app.core.database import SessionLocal
from app.models.category import ProductCategory, ProductSubcategory
from app.models.product import Product
from app.models.rule import ComplianceRule
from app.models.report import ComplianceReport, ViolationDetail
from app.services.compliance_engine import ComplianceEngine

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_25_categories_and_subcategories_seeded(db_session):
    """Verify all 25 major categories and their subcategories exist in DB."""
    cats = db_session.query(ProductCategory).all()
    assert len(cats) >= 25, f"Expected at least 25 categories, found {len(cats)}"

    food_cat = db_session.query(ProductCategory).filter(ProductCategory.name == "Food Products").first()
    assert food_cat is not None
    assert len(food_cat.subcategories) > 0

def test_conditional_rule_false_condition_is_not_applicable(db_session):
    """Verify condition FALSE -> NOT_APPLICABLE, score not reduced."""
    engine = ComplianceEngine(db_session)
    food_cat = db_session.query(ProductCategory).filter(ProductCategory.name == "Food Products").first()
    applicable_rules = engine.retrieve_applicable_rules(food_cat)

    ts = int(time.time() * 1000)
    product = Product(title="Regular Basmati Rice 5kg", url=f"https://example.com/basmati-rice-{ts}", domain="example.com")
    db_session.add(product)
    db_session.flush()

    report = ComplianceReport(product_id=product.id, overall_status="PENDING")
    db_session.add(report)
    db_session.commit()

    # Rice is not fruit beverage, not fortified, not organic, not imported
    attributes = {"subcategory": "Rice / Grains", "is_fortified": False, "is_organic": False, "product_is_imported": False}
    subcategory = db_session.query(ProductSubcategory).filter(ProductSubcategory.name == "Rice / Grains").first()

    declarations = [
        {"key_name": "Product Name", "normalized_value": "Basmati Rice", "confidence_score": 0.95},
        {"key_name": "Manufacturer Name", "normalized_value": "Fortune Foods", "confidence_score": 0.95},
        {"key_name": "Manufacturer Address", "normalized_value": "Ahmedabad, India", "confidence_score": 0.95},
        {"key_name": "Maximum Retail Price (MRP)", "normalized_value": "Rs 499", "confidence_score": 0.95},
        {"key_name": "Country of Origin", "normalized_value": "India", "confidence_score": 0.95},
        {"key_name": "Consumer Care Details", "raw_value": "Consumer Care Email: care@fortune.com", "normalized_value": "Consumer Care Email: care@fortune.com", "confidence_score": 0.95},
        {"key_name": "Net Quantity", "normalized_value": "5 kg", "confidence_score": 0.95},
        {"key_name": "FSSAI License Number", "normalized_value": "10014021000088", "confidence_score": 0.95},
        {"key_name": "Ingredients List / Food Labeling", "normalized_value": "100% Basmati Rice", "confidence_score": 0.95},
        {"key_name": "Nutritional Information", "normalized_value": "Energy 350 kcal", "confidence_score": 0.95},
        {"key_name": "Best Before / Expiry Date", "normalized_value": "Best before 12 months", "confidence_score": 0.95},
        {"key_name": "Date of Manufacture / Packing", "normalized_value": "Pkg Date 01/2026", "confidence_score": 0.95},
        {"key_name": "Batch / Lot Number", "normalized_value": "Batch B-2026X", "confidence_score": 0.95}
    ]

    p_cnt, f_cnt, na_cnt = engine.evaluate_declarations(
        report, applicable_rules, declarations, attributes, subcategory, step_label="HTML"
    )
    engine.compute_score_and_explain(report, product, food_cat, applicable_rules, p_cnt, f_cnt, na_cnt)

    assert na_cnt > 0, "Conditional rules with false conditions must be counted as NOT_APPLICABLE"
    assert report.overall_status == "COMPLIANT", "Product must be COMPLIANT when all applicable mandatory rules pass"
    assert report.overall_score == 100.0, "Score must be 100% excluding NOT_APPLICABLE rules"

    # Cleanup
    db_session.delete(report)
    db_session.delete(product)
    db_session.commit()

def test_cross_category_rule_isolation(db_session):
    """Verify Food does not get electrical rules, Electronics does not get FSSAI rules."""
    engine = ComplianceEngine(db_session)
    food_cat = db_session.query(ProductCategory).filter(ProductCategory.name == "Food Products").first()
    elec_cat = db_session.query(ProductCategory).filter(ProductCategory.name == "Electronics").first()

    food_rules = engine.retrieve_applicable_rules(food_cat)
    elec_rules = engine.retrieve_applicable_rules(elec_cat)

    food_rule_codes = [r.rule_code for r in food_rules]
    elec_rule_codes = [r.rule_code for r in elec_rules]

    assert "LM-ELEC-01" not in food_rule_codes, "Food must not receive electrical rules"
    assert "LM-FOOD-01" not in elec_rule_codes, "Electronics must not receive FSSAI rules"
    assert "LM-CORE-08" not in food_rule_codes, "Food must not receive LM-CORE-08 (Expiry Date)"
    assert "LM-CORE-09" not in food_rule_codes, "Food must not receive LM-CORE-09 (Date of Manufacture/Packing)"

def test_evidence_source_provenance_and_ocr(db_session):
    """Verify evidence source PACKAGE_ONLY distinction and OCR recovery."""
    engine = ComplianceEngine(db_session)
    elec_cat = db_session.query(ProductCategory).filter(ProductCategory.name == "Electronics").first()
    applicable_rules = engine.retrieve_applicable_rules(elec_cat)

    ts = int(time.time() * 1000) + 1
    product = Product(title="Sony Wireless Headphones", url=f"https://example.com/sony-headphones-ocr-{ts}", domain="example.com")
    db_session.add(product)
    db_session.flush()

    report = ComplianceReport(product_id=product.id, overall_status="PENDING")
    db_session.add(report)
    db_session.commit()

    attributes = {"is_electrical": True}
    subcategory = None

    # Initial HTML declarations missing package date
    html_decls = [
        {"key_name": "Product Name", "normalized_value": "Sony Wireless Headphones", "confidence_score": 0.95},
        {"key_name": "Maximum Retail Price (MRP)", "normalized_value": "Rs 4999", "confidence_score": 0.95}
    ]

    p_cnt, f_cnt, na_cnt = engine.evaluate_declarations(report, applicable_rules, html_decls, attributes, subcategory, step_label="HTML")
    
    # Check that package-only violation was recorded with MISSING_FROM_HTML
    mfg_violation = db_session.query(ViolationDetail).join(ComplianceRule).filter(
        ViolationDetail.report_id == report.id,
        ComplianceRule.rule_code == "LM-CORE-09"
    ).first()
    assert mfg_violation is not None
    assert mfg_violation.evidence_status == "MISSING_FROM_HTML"

    # Simulated OCR recovery
    ocr_decls = [
        {"key_name": "Date of Manufacture / Packing", "normalized_value": "01/2026", "confidence_score": 0.90, "source": "ocr"}
    ]
    merged_decls = html_decls + ocr_decls

    db_session.query(ViolationDetail).filter(ViolationDetail.report_id == report.id).delete()
    db_session.commit()

    p_cnt2, f_cnt2, na_cnt2 = engine.evaluate_declarations(report, applicable_rules, merged_decls, attributes, subcategory, step_label="HTML+OCR")

    mfg_violation_post_ocr = db_session.query(ViolationDetail).join(ComplianceRule).filter(
        ViolationDetail.report_id == report.id,
        ComplianceRule.rule_code == "LM-CORE-09"
    ).first()
    assert mfg_violation_post_ocr is not None
    assert mfg_violation_post_ocr.status == "PASSED"
    assert mfg_violation_post_ocr.evidence_status == "FOUND_BY_OCR"

    # Cleanup
    db_session.delete(report)
    db_session.delete(product)
    db_session.commit()
