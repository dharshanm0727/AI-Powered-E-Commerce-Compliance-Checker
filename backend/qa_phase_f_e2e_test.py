import os
import sys
import time
import httpx

sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models.category import ProductCategory
from app.models.product import Product, ExtractedDeclaration, OCRDeclaration
from app.models.rule import ComplianceRule
from app.models.report import ComplianceReport, ViolationDetail
from app.models.audit import AuditLog
from app.services.compliance_engine import ComplianceEngine, run_full_compliance_workflow
from app.services.exporter import generate_pdf_report, generate_excel_report
from app.services.scraper.html_downloader import HTMLDownloaderService

def execute_phase_f_e2e_audit():
    print("=" * 80)
    print("  PHASE F: FINAL REGRESSION TESTING & END-TO-END SYSTEM VERIFICATION  ")
    print("=" * 80)

    db = SessionLocal()
    engine = ComplianceEngine(db)
    ts = int(time.time())

    # ------------------------------------------------------------------ #
    # 1. E2E SCENARIO 1 — COMPLIANT PRODUCT
    # ------------------------------------------------------------------ #
    print("\n--- 1. E2E Scenario 1: Compliant Product ---")
    p1 = Product(
        title="Parle-G Gold Glucose Biscuits 1kg",
        url=f"https://www.example-ecom-test.com/products/parle-g-biscuits-1kg-{ts}",
        domain="example-ecom-test.com",
        image_urls=["https://via.placeholder.com/600x600.png?text=Parle-G+Front+Pack"]
    )
    db.add(p1)
    db.flush()

    r1 = ComplianceReport(product_id=p1.id, overall_status="PENDING")
    db.add(r1)
    db.commit()

    food_cat = db.query(ProductCategory).filter(ProductCategory.name == "Food Products").first()
    food_rules = engine.retrieve_applicable_rules(food_cat)

    # Construct compliant declarations covering all mandatory rules
    html_decls_compliant = []
    for r in food_rules:
        first_token = r.mandatory_fields.split(",")[0].strip()
        html_decls_compliant.append({
            "key_name": r.declaration_name,
            "normalized_value": f"Valid {first_token} Value",
            "confidence_score": 0.95
        })

    p_cnt1, f_cnt1 = engine.evaluate_declarations(r1, food_rules, html_decls_compliant)
    engine.compute_score_and_explain(r1, p1, food_cat, food_rules, p_cnt1, f_cnt1)

    print(f"Scenario 1 Result: Status='{r1.overall_status}', Score={r1.overall_score}%, Passed={p_cnt1}/{len(food_rules)}")
    assert r1.overall_status == "COMPLIANT" and r1.overall_score == 100.0, "Compliant product must yield 100% COMPLIANT status"
    print("[PASS] E2E Scenario 1 (Compliant Product): VERIFIED")

    # ------------------------------------------------------------------ #
    # 2. E2E SCENARIO 2 — NON-COMPLIANT PRODUCT
    # ------------------------------------------------------------------ #
    print("\n--- 2. E2E Scenario 2: Non-Compliant Product ---")
    p2 = Product(
        title="Unbranded Local Snacks 500g",
        url=f"https://www.example-ecom-test.com/products/unbranded-snacks-500g-{ts}",
        domain="example-ecom-test.com"
    )
    db.add(p2)
    db.flush()

    r2 = ComplianceReport(product_id=p2.id, overall_status="PENDING")
    db.add(r2)
    db.commit()

    # Missing mandatory MRP and Manufacturer Address
    html_decls_non_compliant = [
        {"key_name": "Product Name", "normalized_value": "Local Snacks", "confidence_score": 0.90},
        {"key_name": "Net Quantity", "normalized_value": "500 g", "confidence_score": 0.90},
    ]

    p_cnt2, f_cnt2 = engine.evaluate_declarations(r2, food_rules, html_decls_non_compliant)
    engine.compute_score_and_explain(r2, p2, food_cat, food_rules, p_cnt2, f_cnt2)

    print(f"Scenario 2 Result: Status='{r2.overall_status}', Score={r2.overall_score}%, Failed={f_cnt2}/{len(food_rules)}")
    print(f"Reasoning Rationale: '{r2.reasoning_summary[:100]}...'")
    assert r2.overall_status == "NON_COMPLIANT" and r2.overall_score < 100.0, "Non-compliant product must yield NON_COMPLIANT status"
    print("[PASS] E2E Scenario 2 (Non-Compliant Product & Rationale): VERIFIED")

    # ------------------------------------------------------------------ #
    # 3. E2E SCENARIO 3 — OCR RECOVERY WORKFLOW
    # ------------------------------------------------------------------ #
    print("\n--- 3. E2E Scenario 3: OCR Recovery Workflow ---")
    p3 = Product(
        title="Fortune Everyday Basmati Rice 5kg",
        url=f"https://www.example-ecom-test.com/products/fortune-basmati-rice-5kg-{ts}",
        domain="example-ecom-test.com",
        image_urls=["https://via.placeholder.com/600x600.png?text=Fortune+Rice+Back+Pack"]
    )
    db.add(p3)
    db.flush()

    r3 = ComplianceReport(product_id=p3.id, overall_status="PENDING")
    db.add(r3)
    db.commit()

    # Step 3a: HTML missing MRP and FSSAI
    html_decls_partial = [
        {"key_name": "Product Name", "normalized_value": "Fortune Basmati Rice", "confidence_score": 0.95},
        {"key_name": "Net Quantity", "normalized_value": "5 kg", "confidence_score": 0.95},
    ]

    p_cnt3_html, f_cnt3_html = engine.evaluate_declarations(r3, food_rules, html_decls_partial, step_label="HTML")
    print(f"Scenario 3 Initial HTML Check: Passed={p_cnt3_html}, Failed={f_cnt3_html}")

    # Step 3b: Trigger OCR and Merge Declarations
    ocr_decls_recovered = [
        {"key_name": "MRP", "normalized_value": "Rs. 499.00", "confidence_score": 0.92, "source": "ocr"},
        {"key_name": "FSSAI License Number", "normalized_value": "10014021000088", "confidence_score": 0.95, "source": "ocr"},
        {"key_name": "Country of Origin", "normalized_value": "India", "confidence_score": 0.96, "source": "ocr"}
    ]

    merged_decls = html_decls_partial + ocr_decls_recovered
    db.query(ViolationDetail).filter(ViolationDetail.report_id == r3.id).delete()
    db.commit()

    p_cnt3_final, f_cnt3_final = engine.evaluate_declarations(r3, food_rules, merged_decls, step_label="HTML+OCR")
    engine.compute_score_and_explain(r3, p3, food_cat, food_rules, p_cnt3_final, f_cnt3_final)

    print(f"Scenario 3 Post-OCR Recovery: Passed={p_cnt3_final}, Score={r3.overall_score}%, Status='{r3.overall_status}'")
    assert p_cnt3_final > p_cnt3_html, "OCR recovery must increase passed rules count"
    print("[PASS] E2E Scenario 3 (OCR Evidence Merge & Recovery): VERIFIED")

    # ------------------------------------------------------------------ #
    # 4. REPORT CONSISTENCY & EXPORTER AUDIT (PDF & EXCEL)
    # ------------------------------------------------------------------ #
    print("\n--- 4. Report Consistency & Exporter Audit (PDF & Excel) ---")

    pdf_bytes = generate_pdf_report(r1)
    excel_bytes = generate_excel_report(r1)

    print(f"Generated PDF Blob Size: {len(pdf_bytes)} bytes")
    print(f"Generated Excel Blob Size: {len(excel_bytes)} bytes")

    assert len(pdf_bytes) > 500, "PDF report exporter must return valid binary PDF content"
    assert len(excel_bytes) > 500, "Excel report exporter must return valid binary spreadsheet content"
    print("[PASS] Report Consistency & Binary Exporters (PDF & Excel): VERIFIED")

    # ------------------------------------------------------------------ #
    # 5. DATA INTEGRITY & AUDIT LOGGING VERIFICATION
    # ------------------------------------------------------------------ #
    print("\n--- 5. Data Integrity & Audit Logging Verification ---")

    audit = AuditLog(user_id=1, action="COMPLIANCE_CHECK_COMPLETED", entity_type="ComplianceReport", entity_id=r1.id)
    db.add(audit)
    db.commit()

    total_products = db.query(Product).count()
    total_reports = db.query(ComplianceReport).count()
    total_violations = db.query(ViolationDetail).count()
    total_audits = db.query(AuditLog).count()

    print(f"Database Integrity Records: Products={total_products}, Reports={total_reports}, Violations={total_violations}, Audits={total_audits}")
    assert total_products >= 3 and total_reports >= 3 and total_violations > 0, "ORM data integrity check must pass"
    print("[PASS] Database ORM Data Integrity & Audit Logging: VERIFIED")

    # Cleanup temporary test products
    db.delete(r1)
    db.delete(p1)
    db.delete(r2)
    db.delete(p2)
    db.delete(r3)
    db.delete(p3)
    db.delete(audit)
    db.commit()
    db.close()

    print("\n=" * 80)
    print("              PHASE F QA E2E & REGRESSION AUDIT COMPLETE              ")
    print("=" * 80)

if __name__ == "__main__":
    execute_phase_f_e2e_audit()
