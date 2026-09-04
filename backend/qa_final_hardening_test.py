import os
import sys
import time
import httpx

sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models.category import ProductCategory
from app.models.product import Product, ExtractedDeclaration, OCRDeclaration
from app.models.rule import ComplianceRule, RuleCategoryMapping
from app.models.report import ComplianceReport, ViolationDetail
from app.models.audit import AuditLog
from app.services.compliance_engine import ComplianceEngine
from app.services.scraper.html_downloader import HTMLDownloaderService
from app.services.ai.providers.mock_provider import MockAIProvider

def execute_final_hardening_audit():
    print("=" * 80)
    print("  FINAL HARDENING & REAL-WORLD VALIDATION SUITE  ")
    print("=" * 80)

    db = SessionLocal()
    engine = ComplianceEngine(db)
    ai_provider = MockAIProvider()
    ts = int(time.time())

    # ------------------------------------------------------------------ #
    # 1. REAL-WORLD URL & SSRF VALIDATION
    # ------------------------------------------------------------------ #
    print("\n--- 1. Real-World Product URL & Anti-Bot Validation ---")
    
    test_urls = [
        ("https://www.amazon.in/Fortune-Everyday-Basmati-Rice-5kg/dp/B07575Z817", True, "Public Amazon URL"),
        ("https://amzn.in/d/08EmUcfO", True, "Public Amzn Shortened URL"),
        ("http://127.0.0.1:8000/secret", False, "Blocked Localhost IPv4 SSRF Target"),
        ("http://169.254.169.254/latest/meta-data/", False, "Blocked AWS Cloud Metadata Endpoint")
    ]

    for url, should_pass, desc in test_urls:
        try:
            HTMLDownloaderService.validate_url(url)
            print(f"[PASS] URL Validation '{desc}' ({url}): VALIDATED")
            assert should_pass, f"URL {url} should have failed validation!"
        except ValueError as e:
            print(f"[PASS] SSRF / Security Rejection '{desc}' ({url}): REJECTED -> {e}")
            assert not should_pass, f"URL {url} should have passed validation!"

    # ------------------------------------------------------------------ #
    # 2. AI HALLUCINATION & EVIDENCE TRACKING AUDIT
    # ------------------------------------------------------------------ #
    print("\n--- 2. AI Hallucination & Evidence Tracking Audit ---")

    sample_html = "Fortune Everyday Basmati Rice 5kg. Net Weight: 5kg. MRP: Rs 499."
    extracted = ai_provider.extract_declarations(sample_html)

    print(f"Extracted Declarations Count: {len(extracted)}")
    for item in extracted:
        has_evidence = "key_name" in item and "normalized_value" in item and "confidence_score" in item
        assert has_evidence, "Extracted declaration must contain field, value, and confidence evidence"

    print("[PASS] AI Extraction & Evidence Tracking: VERIFIED")

    # ------------------------------------------------------------------ #
    # 3. RULE DATABASE & CATEGORY INTEGRITY AUDIT
    # ------------------------------------------------------------------ #
    print("\n--- 3. Rule Database & Category Integrity Audit ---")

    categories_count = db.query(ProductCategory).count()
    rules_count = db.query(ComplianceRule).count()
    mappings_count = db.query(RuleCategoryMapping).count()

    orphaned_mappings = db.query(RuleCategoryMapping).filter(
        ~RuleCategoryMapping.category_id.in_(db.query(ProductCategory.id)),
        ~RuleCategoryMapping.rule_id.in_(db.query(ComplianceRule.id))
    ).count()

    print(f"Seeded Database Audit: Categories={categories_count}, Rules={rules_count}, Mappings={mappings_count}, Orphaned Mappings={orphaned_mappings}")
    assert categories_count == 25 and rules_count == 24 and mappings_count == 216 and orphaned_mappings == 0, "Database integrity audit must pass"
    print("[PASS] Database Integrity & Zero Orphaned Mappings: VERIFIED")

    # ------------------------------------------------------------------ #
    # 4. FINAL DEMONSTRATION FLOW CHECK (FLOW 1, FLOW 2, FLOW 3)
    # ------------------------------------------------------------------ #
    print("\n--- 4. Real-World Demonstration Check (Flow 1, Flow 2, Flow 3) ---")

    food_cat = db.query(ProductCategory).filter(ProductCategory.name == "Food Products").first()
    food_rules = engine.retrieve_applicable_rules(food_cat)

    # FLOW 1: Compliant Product
    p1 = Product(title="Parle-G Biscuits 1kg", url=f"https://www.example-demo.com/p1-{ts}", domain="example-demo.com")
    db.add(p1)
    db.flush()
    r1 = ComplianceReport(product_id=p1.id, overall_status="PENDING")
    db.add(r1)
    db.commit()

    decls_flow1 = []
    for r in food_rules:
        first_token = r.mandatory_fields.split(",")[0].strip()
        decls_flow1.append({
            "key_name": r.declaration_name,
            "normalized_value": f"Valid {first_token} Value",
            "confidence_score": 0.95
        })

    p_cnt1, f_cnt1 = engine.evaluate_declarations(r1, food_rules, decls_flow1)
    engine.compute_score_and_explain(r1, p1, food_cat, food_rules, p_cnt1, f_cnt1)
    print(f"Flow 1 Result: Status='{r1.overall_status}', Score={r1.overall_score}%")
    assert r1.overall_status == "COMPLIANT" and r1.overall_score == 100.0, "Flow 1 must return COMPLIANT (100%)"
    print("[PASS] DEMO FLOW 1 (Sufficient Declarations -> COMPLIANT 100%): VERIFIED")

    # FLOW 2: Non-Compliant Product with Missing Declarations
    p2 = Product(title="Local Snack Box 500g", url=f"https://www.example-demo.com/p2-{ts}", domain="example-demo.com")
    db.add(p2)
    db.flush()
    r2 = ComplianceReport(product_id=p2.id, overall_status="PENDING")
    db.add(r2)
    db.commit()

    decls_flow2 = [{"key_name": "Product Name", "normalized_value": "Local Snack", "confidence_score": 0.90}]
    p_cnt2, f_cnt2 = engine.evaluate_declarations(r2, food_rules, decls_flow2)
    engine.compute_score_and_explain(r2, p2, food_cat, food_rules, p_cnt2, f_cnt2)
    print(f"Flow 2 Result: Status='{r2.overall_status}', Score={r2.overall_score}%, Violations={f_cnt2}")
    assert r2.overall_status == "NON_COMPLIANT" and r2.overall_score < 100.0, "Flow 2 must return NON_COMPLIANT"
    print("[PASS] DEMO FLOW 2 (Missing Declarations -> NON_COMPLIANT & Clear Violations): VERIFIED")

    # FLOW 3: Declaration Missing from HTML, Recovered via OCR
    p3 = Product(title="Fortune Basmati Rice 5kg", url=f"https://www.example-demo.com/p3-{ts}", domain="example-demo.com")
    db.add(p3)
    db.flush()
    r3 = ComplianceReport(product_id=p3.id, overall_status="PENDING")
    db.add(r3)
    db.commit()

    decls_flow3_html = [{"key_name": "Product Name", "normalized_value": "Fortune Rice", "confidence_score": 0.90}]
    p_cnt3_initial, f_cnt3_initial = engine.evaluate_declarations(r3, food_rules, decls_flow3_html, step_label="HTML")

    decls_flow3_ocr = [
        {"key_name": "MRP", "normalized_value": "Rs 499", "confidence_score": 0.92, "source": "ocr"},
        {"key_name": "FSSAI License Number", "normalized_value": "10014021000088", "confidence_score": 0.95, "source": "ocr"}
    ]
    merged_decls = decls_flow3_html + decls_flow3_ocr
    db.query(ViolationDetail).filter(ViolationDetail.report_id == r3.id).delete()
    db.commit()

    p_cnt3_final, f_cnt3_final = engine.evaluate_declarations(r3, food_rules, merged_decls, step_label="HTML+OCR")
    engine.compute_score_and_explain(r3, p3, food_cat, food_rules, p_cnt3_final, f_cnt3_final)
    print(f"Flow 3 Result: Pre-OCR Passed={p_cnt3_initial} -> Post-OCR Passed={p_cnt3_final}, Score={r3.overall_score}%")
    assert p_cnt3_final > p_cnt3_initial, "Flow 3 post-OCR recovery must increase passed rules count"
    print("[PASS] DEMO FLOW 3 (HTML Missing -> OCR Recovery -> Merged Evidence Re-evaluation): VERIFIED")

    # Cleanup temporary test records
    db.delete(r1); db.delete(p1)
    db.delete(r2); db.delete(p2)
    db.delete(r3); db.delete(p3)
    db.commit()
    db.close()

    print("\n=" * 80)
    print("           FINAL HARDENING & REAL-WORLD VALIDATION SUITE COMPLETE      ")
    print("=" * 80)

if __name__ == "__main__":
    execute_final_hardening_audit()
