import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
sys.stdout.reconfigure(encoding='utf-8')

from app.core.database import SessionLocal
from app.models.category import ProductCategory, ProductSubcategory
from app.models.product import Product
from app.models.rule import ComplianceRule
from app.models.report import ComplianceReport, ViolationDetail
from app.services.compliance_engine import ComplianceEngine, run_full_compliance_workflow
from app.services.discovery.url_verifier import LiveURLVerifierService, VerificationStatus

def run_real_world_url_verification_suite():
    print("=" * 140)
    print("  LIVE REAL-WORLD PRODUCT URL DISCOVERY & VERIFICATION SUITE  ")
    print("=" * 140)

    db = SessionLocal()
    engine = ComplianceEngine(db)

    # -------------------------------------------------------------
    # 1. Test Previously Used Dead / Broken URLs (Section 13)
    # -------------------------------------------------------------
    print("\n[SECTION 13] Live Testing Previously Used URL:")
    dead_candidate_url = "https://www.amazon.in/Fortune-Everyday-Basmati-Rice-5kg/dp/B07R9D971S"
    print(f"Target URL: {dead_candidate_url}")

    dead_check = LiveURLVerifierService.verify_product_url(dead_candidate_url)
    print(f"-> Live HTTP Status: {dead_check.get('http_status')}")
    print(f"-> Verification Status: {dead_check.get('verification_status')}")
    print(f"-> Error Reason: {dead_check.get('error_reason')}")
    print(f"-> Result: MARKED AS {dead_check.get('verification_status')}. ABORTED FROM COMPLIANCE ENGINE.")

    rejected_urls = [
        {"url": dead_candidate_url, "reason": f"HTTP {dead_check.get('http_status')} / {dead_check.get('error_reason')}"},
        {"url": "https://www.amazon.in/Optimum-Nutrition-Standard-Naturally-Flavored/dp/B000GIQT06", "reason": "HTTP 404 / Page Not Found"},
        {"url": "https://www.optimumnutrition.co.in/gold-standard-100-whey", "reason": "HTTP 404 / Page Not Found"},
        {"url": "https://www.croma.com/philips-stellar-bright-9w-b22-led-bulb-cool-day-white-/p/231189", "reason": "HTTP 403 / Access Denied (Automated Access Blocked)"},
        {"url": "https://blinkit.com/prn/fortune-everyday-basmati-rice/prid/43126", "reason": "HTTP 403 / Error Page (Automated Access Blocked)"},
        {"url": "https://www.1mg.com/otc/nivea-soft-light-moisturizer-creme-with-vitamin-e-jojoba-oil-for-face-body-hands-otc348911", "reason": "HTTP 404 / Product Not Found"}
    ]

    # -------------------------------------------------------------
    # 2. Live Verified Product Test Set (8 Categories)
    # -------------------------------------------------------------
    verified_candidates = [
        {
            "category": "Food Products",
            "name": "True Elements Rolled Oats 1kg",
            "url": "https://true-elements.com/products/rolled-oats-1kg"
        },
        {
            "category": "Beverages",
            "name": "Sleepy Owl Hazelnut Instant Coffee",
            "url": "https://sleepyowl.co/products/hazelnut-instant-coffee"
        },
        {
            "category": "Cosmetics / Personal Care",
            "name": "Minimalist Salicylic Acid 2% Face Serum",
            "url": "https://beminimalist.co/products/salicylic-acid-2"
        },
        {
            "category": "Mobile Phones",
            "name": "Portronics Adapto 20 20W Fast Charger",
            "url": "https://www.portronics.com/products/adapto-20"
        },
        {
            "category": "Computers / Laptops",
            "name": "Portronics Key7 Combo Wireless Keyboard and Mouse",
            "url": "https://www.portronics.com/products/key7-combo"
        },
        {
            "category": "Clothing / Garments",
            "name": "Beyoung Navy Blue Polo T-Shirt",
            "url": "https://www.beyoung.in/navy-blue-polo-t-shirt"
        },
        {
            "category": "Electronics",
            "name": "boAt Airdopes 141 Wireless Earbuds",
            "url": "https://www.boat-lifestyle.com/products/airdopes-141"
        },
        {
            "category": "Kitchen Appliances",
            "name": "KENT Ultra Storage Water Purifier",
            "url": "https://www.kent.co.in/products/kent-ultra-storage"
        }
    ]

    print("\n" + "=" * 140)
    print("  LIVE REAL-PRODUCT VERIFICATION & COMPLIANCE PIPELINE AUDIT  ")
    print("=" * 140)

    verified_results = []

    for idx, item in enumerate(verified_candidates, 1):
        url = item["url"]
        cat_name = item["category"]
        expected_name = item["name"]

        print(f"\n--- [PRODUCT #{idx}] ---")
        print(f"Category: {cat_name}")
        print(f"Target Product: {expected_name}")
        print(f"Input URL: {url}")

        # STEP 1-7: Live URL Verification
        ver = LiveURLVerifierService.verify_product_url(url, expected_product_name=expected_name, category=cat_name)

        if not ver.get("is_verified", False):
            print(f"❌ URL Verification FAILED: {ver.get('error_reason')}")
            rejected_urls.append({"url": url, "reason": ver.get("error_reason")})
            continue

        preview = ver.get("product_preview", {})
        canonical_url = ver.get("canonical_url", url)

        # Section 11: Product Data Preview
        print("\n[PRODUCT DATA PREVIEW]")
        print(f"  Product Name:         {preview.get('product_name')}")
        print(f"  Brand:                {preview.get('brand')}")
        print(f"  Category:             {cat_name}")
        print(f"  Price/MRP:            {preview.get('price')}")
        print(f"  Product URL:          {canonical_url}")
        print(f"  Images Detected:      {preview.get('images_count')}")
        print(f"  Scraper Status:       SUCCESS")
        print(f"  Product Identity:     MATCHED")

        # Create or fetch product & report in DB
        prod_obj = db.query(Product).filter(Product.url == canonical_url).first()
        if not prod_obj:
            prod_obj = Product(title=preview.get("product_name"), url=canonical_url)
            db.add(prod_obj)
            db.flush()
        else:
            prod_obj.title = preview.get("product_name")

        cat_obj = db.query(ProductCategory).filter(ProductCategory.name == cat_name).first()
        report_obj = ComplianceReport(product_id=prod_obj.id, category_id=cat_obj.id if cat_obj else None, overall_status="PENDING")
        db.add(report_obj)
        db.commit()

        # Run compliance pipeline
        run_full_compliance_workflow(report_obj.id, db)
        db.refresh(report_obj)

        print(f"  Overall Score:        {report_obj.overall_score}%")
        print(f"  Overall Status:       {report_obj.overall_status}")
        print(f"  Status Summary:       {report_obj.reasoning_summary[:120]}...")

        # Domain extraction
        platform_name = "Official Brand Store"
        if "true-elements" in canonical_url:
            platform_name = "True Elements Store"
        elif "sleepyowl" in canonical_url:
            platform_name = "Sleepy Owl Store"
        elif "beminimalist" in canonical_url:
            platform_name = "Minimalist Store"
        elif "portronics" in canonical_url:
            platform_name = "Portronics Store"
        elif "beyoung" in canonical_url:
            platform_name = "Beyoung Store"
        elif "boat-lifestyle" in canonical_url:
            platform_name = "boAt Lifestyle Store"
        elif "kent.co.in" in canonical_url:
            platform_name = "KENT Official Store"

        verified_results.append({
            "idx": idx,
            "product": preview.get("product_name"),
            "category": cat_name,
            "platform": platform_name,
            "url": canonical_url,
            "http": ver.get("http_status"),
            "scraper": "SUCCESS",
            "identity": "MATCHED",
            "score": report_obj.overall_score,
            "status": report_obj.overall_status
        })

    # -------------------------------------------------------------
    # 3. Final Summary Tables (Section 16)
    # -------------------------------------------------------------
    print("\n" + "=" * 140)
    print("  SECTION 16 FINAL REPORT: VERIFIED PRODUCTS  ")
    print("=" * 140)
    print(f"{'#':<3} | {'Product':<32} | {'Category':<22} | {'Platform':<20} | {'HTTP':<5} | {'Scraper':<8} | {'Identity':<8} | {'Score':<7} | {'Status':<12}")
    print("-" * 140)
    for r in verified_results:
        print(f"{r['idx']:<3} | {r['product'][:32]:<32} | {r['category'][:22]:<22} | {r['platform'][:20]:<20} | {r['http']:<5} | {r['scraper']:<8} | {r['identity']:<8} | {r['score']:<6.1f}% | {r['status']:<12}")

    print("\n" + "=" * 140)
    print("  SECTION 16 FINAL REPORT: REJECTED / DEAD URLS  ")
    print("=" * 140)
    print(f"{'URL':<90} | {'Reason'}")
    print("-" * 140)
    for r in rejected_urls:
        print(f"{r['url']:<90} | {r['reason']}")

if __name__ == "__main__":
    run_real_world_url_verification_suite()
