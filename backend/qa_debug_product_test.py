import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models.category import ProductCategory, ProductSubcategory
from app.models.product import Product
from app.models.rule import ComplianceRule
from app.models.report import ComplianceReport, ViolationDetail
from app.services.compliance_engine import ComplianceEngine

def run_critical_debug_product_test():
    print("=" * 140)
    print("  CRITICAL DEBUG — REAL PRODUCT EVALUATION & FIELD EVIDENCE AUDIT REPORT (SECTION 14)  ")
    print("=" * 140)

    db = SessionLocal()
    engine = ComplianceEngine(db)
    ts = int(time.time())

    # Real Product under test: Optimum Nutrition Gold Standard 100% Whey Protein 1kg
    product_title = "Optimum Nutrition Gold Standard 100% Whey Protein 1kg"
    cat_obj = db.query(ProductCategory).filter(ProductCategory.name == "Health Supplements / Nutraceuticals").first()
    sub_obj = db.query(ProductSubcategory).filter(ProductSubcategory.name == "Protein Powder").first()

    p = Product(title=product_title, url=f"https://www.optimumnutrition.co.in/gold-standard-100-whey/demo-{ts}", domain="optimumnutrition.co.in")
    db.add(p)
    db.flush()

    r = ComplianceReport(product_id=p.id, category_id=cat_obj.id, overall_status="PENDING")
    if sub_obj:
        r.subcategory_id = sub_obj.id
    db.add(r)
    db.commit()

    applicable_rules = engine.retrieve_applicable_rules(cat_obj)
    attrs = {"subcategory": "Protein Powder", "product_is_imported": True}

    # Simulate realistic HTML listing scrape (where MRP is present in HTML, but package fields like Mfg Date & Batch No are missing from HTML prior to OCR)
    html_declarations = [
        {"key_name": "Product Name", "normalized_value": "Optimum Nutrition Gold Standard 100% Whey Protein 1kg", "confidence_score": 0.95, "source": "html"},
        {"key_name": "Manufacturer Name", "normalized_value": "Optimum Nutrition Inc", "confidence_score": 0.95, "source": "html"},
        {"key_name": "Manufacturer Address", "normalized_value": "Glanbia Performance Nutrition India Pvt Ltd, Gurgaon", "confidence_score": 0.95, "source": "html"},
        {"key_name": "Maximum Retail Price (MRP)", "normalized_value": "Rs. 3899", "confidence_score": 0.95, "source": "html"},
        {"key_name": "Country of Origin", "normalized_value": "India", "confidence_score": 0.95, "source": "html"},
        {"key_name": "Consumer Care Details", "raw_value": "india.support@glanbia.com, 1800-103-5449", "normalized_value": "india.support@glanbia.com", "confidence_score": 0.95, "source": "html"},
        {"key_name": "Net Quantity", "normalized_value": "1 kg", "confidence_score": 0.95, "source": "html"},
        {"key_name": "FSSAI License Number", "normalized_value": "10014011000201", "confidence_score": 0.99, "source": "html"},
        {"key_name": "Ingredients List / Food Labeling", "normalized_value": "Whey Protein Isolate, Whey Protein Concentrate, Cocoa", "confidence_score": 0.95, "source": "html"},
        {"key_name": "Nutritional Information", "normalized_value": "Protein 24g, BCAAs 5.5g per serving", "confidence_score": 0.95, "source": "html"}
    ]

    p_cnt, f_cnt, na_cnt = engine.evaluate_declarations(r, applicable_rules, html_declarations, attrs, sub_obj, step_label="HTML")
    engine.compute_score_and_explain(r, p, cat_obj, applicable_rules, p_cnt, f_cnt, na_cnt)

    print(f"\nProduct: {product_title}")
    print(f"Category: {cat_obj.name}")
    print(f"Subcategory: {sub_obj.name if sub_obj else 'General'}")
    print(f"Overall Compliance Score: {r.overall_score}%")
    print(f"Overall Status: {r.overall_status}\n")

    print(f"{'Rule Code':<12} | {'Rule Name':<32} | {'Applicability':<15} | {'Evidence Source':<20} | {'HTML Value':<18} | {'Final Rule Status':<18} | {'Reason'}")
    print("-" * 140)

    all_violations = db.query(ViolationDetail).filter(ViolationDetail.report_id == r.id).all()
    violation_map = {v.rule_id: v for v in all_violations}

    for rule in applicable_rules:
        v = violation_map.get(rule.id)
        is_app = engine.is_rule_applicable(rule, attrs, sub_obj)
        app_str = "Applicable" if is_app else "NOT_APPLICABLE"
        html_val = v.actual_found if (v and v.actual_found) else "Not Found"
        status_str = v.status if v else "UNKNOWN"
        reason = v.ai_reasoning if v else ""

        print(f"{rule.rule_code:<12} | {rule.declaration_name:<32} | {app_str:<15} | {rule.evidence_source:<20} | {html_val[:18]:<18} | {status_str:<18} | {reason[:40]}")

if __name__ == "__main__":
    run_critical_debug_product_test()
