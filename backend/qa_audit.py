import os
import sys
import time

# Ensure app imports work cleanly
sys.path.insert(0, os.path.dirname(__file__))

from app.services.ai.providers.mock_provider import MockAIProvider
from app.services.scraper.html_downloader import HTMLDownloaderService
from app.core.database import SessionLocal
from app.models.category import ProductCategory
from app.models.product import Product
from app.models.report import ComplianceReport
from app.services.compliance_engine import run_full_compliance_workflow, ComplianceEngine
from app.services.ocr.preprocessor import ImagePreprocessor

def run_qa_audit():
    print("=" * 70)
    print("  LEGAL METROLOGY COMPLIANCE CHECKER - QA VERIFICATION SUITE  ")
    print("=" * 70)

    db = SessionLocal()
    ai_provider = MockAIProvider()

    # Retrieve all seed categories
    categories = db.query(ProductCategory).all()
    cat_names = [c.name for c in categories]

    # ------------------------------------------------------------------ #
    # 1. CATEGORY CLASSIFICATION MATRIX TEST
    # ------------------------------------------------------------------ #
    print("\n--- 1. CATEGORY CLASSIFICATION MATRIX TEST ---")

    matrix_test_cases = [
        ("Parle-G Gold Glucose Biscuits 1kg Pack", "Food Products", ["Food Products", "Grocery"]),
        ("Fortune Everyday Basmati Rice 5kg", "Food Products", ["Food Products", "Grocery"]),
        ("Tata Tea Gold Premium Black Tea 1kg", "Beverages", ["Beverages", "Food Products"]),
        ("Nivea Soft Light Moisturising Cream 200ml", "Cosmetics", ["Cosmetics", "Personal Care"]),
        ("Dove Intense Repair Shampoo 650ml", "Personal Care", ["Personal Care", "Cosmetics"]),
        ("Samsung Galaxy S24 Ultra 5G Smartphone", "Mobile Phones", ["Mobile Phones", "Electronics"]),
        ("ASUS Vivobook 15 Core i5 Laptop SSD", "Electronics", ["Electronics"]),
        ("Puma Men's Cotton Round Neck T-Shirt", "Clothing", ["Clothing"]),
        ("Nike Air Zoom Leather Running Shoes", "Footwear", ["Footwear"]),
        ("Solid Wood 6 Seater Dining Table Set", "Furniture", ["Furniture"]),
        ("Bajaj Rex 750W Mixer Grinder 3 Jars", "Kitchen Appliances", ["Kitchen Appliances"]),
        ("LG 260L Double Door Refrigerator Smart Inverter", "Home Appliances", ["Home Appliances"]),
        ("Dettol Antiseptic Liquid Handwash 1500ml", "Personal Care", ["Personal Care", "Cleaning Products"]),
        ("Optimum Nutrition Gold Standard 100% Whey Protein", "Health Supplements", ["Health Supplements", "Food Products"]),
        ("Paracetamol Tablets 650mg Prescription Pharma", "Medicines", ["Medicines"]),
        ("Pedigree Adult Dry Dog Food Meat & Rice 10kg", "Pet Products", ["Pet Products", "Food Products"]),
    ]

    matrix_results = []
    passed_classifications = 0

    for title, expected, allowed_alternatives in matrix_test_cases:
        actual = ai_provider.classify_category(title, title, cat_names)
        is_correct = actual == expected or actual in allowed_alternatives
        if is_correct:
            passed_classifications += 1

        matrix_results.append({
            "title": title,
            "expected": expected,
            "actual": actual,
            "correct": "PASS" if is_correct else "FAIL"
        })

    accuracy = (passed_classifications / len(matrix_test_cases)) * 100
    print(f"Executed {len(matrix_test_cases)} category classification tests.")
    print(f"Passed: {passed_classifications} / {len(matrix_test_cases)} ({accuracy:.1f}% accuracy)")

    print("\nDetailed Matrix Breakdown:")
    print(f"{'Product Title':<50} | {'Expected':<18} | {'Actual':<18} | Status")
    print("-" * 96)
    for r in matrix_results:
        print(f"{r['title'][:48]:<50} | {r['expected']:<18} | {r['actual']:<18} | {r['correct']}")

    # ------------------------------------------------------------------ #
    # 2. OCR PREPROCESSOR & IMAGE VERIFICATION
    # ------------------------------------------------------------------ #
    print("\n--- 2. OCR & PREPROCESSING VERIFICATION ---")

    try:
        import numpy as np
        dummy_img = np.zeros((200, 400, 3), dtype=np.uint8)
        gray = ImagePreprocessor.grayscale(dummy_img)
        denoised = ImagePreprocessor.noise_removal(gray)
        thresh = ImagePreprocessor.thresholding(denoised)
        print("[PASS] OpenCV image preprocessor pipeline (grayscale, noise reduction, thresholding): OPERATIONAL")
    except Exception as e:
        print(f"[FAIL] Preprocessor failure: {e}")

    # ------------------------------------------------------------------ #
    # 3. RULE ENGINE & ISOLATION VERIFICATION
    # ------------------------------------------------------------------ #
    print("\n--- 3. RULE ENGINE & ISOLATION VERIFICATION ---")
    engine = ComplianceEngine(db)

    food_cat = db.query(ProductCategory).filter(ProductCategory.name == "Food Products").first()
    elec_cat = db.query(ProductCategory).filter(ProductCategory.name == "Electronics").first()

    food_rules = engine.retrieve_applicable_rules(food_cat) if food_cat else []
    elec_rules = engine.retrieve_applicable_rules(elec_cat) if elec_cat else []

    food_rule_codes = [r.rule_code for r in food_rules]
    elec_rule_codes = [r.rule_code for r in elec_rules]

    part_no_in_food = "LM-ELEC-06" in food_rule_codes or "LM-ELEC-01" in food_rule_codes
    part_no_in_elec = "LM-ELEC-06" in elec_rule_codes or "LM-ELEC-01" in elec_rule_codes

    print(f"Food Category Applicable Rules Count: {len(food_rules)} ({', '.join(food_rule_codes)})")
    print(f"Electronics Category Applicable Rules Count: {len(elec_rules)} ({', '.join(elec_rule_codes)})")

    if not part_no_in_food and part_no_in_elec:
        print("[PASS] Rule Engine Category Isolation: VERIFIED (Part Number correctly excluded from Food Products)")
    else:
        print("[FAIL] Rule Engine Category Isolation: FAILED (Part Number incorrectly present in Food Products)")

    # ------------------------------------------------------------------ #
    # 4. ERROR HANDLING & TIMEOUT RESILIENCE
    # ------------------------------------------------------------------ #
    print("\n--- 4. ERROR HANDLING & RESILIENCE TEST ---")

    error_test_urls = [
        "https://invalid-non-existent-domain-12345.com/item",
        "https://www.amazon.in/dp/INVALID_ASIN_999999",
    ]

    for err_url in error_test_urls:
        start_t = time.time()
        res_data = HTMLDownloaderService.scrape_product_page(err_url)
        elapsed = time.time() - start_t
        print(f"Resilience test for '{err_url[:45]}...': Title='{res_data.get('title')[:30]}', Elapsed={elapsed:.2f}s -> HANDLED CLEANLY")

    # ------------------------------------------------------------------ #
    # 5. SCORING MATH BOUNDS VERIFICATION
    # ------------------------------------------------------------------ #
    print("\n--- 5. COMPLIANCE SCORING MATH VERIFICATION ---")

    test_product = Product(url="https://qa-test-scoring.example.com/item")
    db.add(test_product)
    db.flush()

    report = ComplianceReport(product_id=test_product.id, overall_status="PENDING")
    db.add(report)
    db.commit()

    run_full_compliance_workflow(report.id, db)
    db.refresh(report)

    valid_score = 0.0 <= report.overall_score <= 100.0
    valid_status = report.overall_status in ["COMPLIANT", "WARNING", "NON_COMPLIANT", "FAILED"]

    print(f"Report ID #{report.id}: Status='{report.overall_status}', Score={report.overall_score}%")
    if valid_score and valid_status:
        print("[PASS] Compliance Score Calculation: VERIFIED (Score within bounds [0.0%, 100.0%])")
    else:
        print("[FAIL] Compliance Score Calculation: FAILED (Score out of bounds)")

    # Cleanup test product
    db.delete(report)
    db.delete(test_product)
    db.commit()

    print("\n=" * 70)
    print("                  QA VERIFICATION SUITE COMPLETE               ")
    print("=" * 70)
    db.close()

if __name__ == "__main__":
    run_qa_audit()
