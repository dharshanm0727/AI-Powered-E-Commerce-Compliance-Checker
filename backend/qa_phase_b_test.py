import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models.category import ProductCategory
from app.services.ai.providers.mock_provider import MockAIProvider

def execute_phase_b():
    db = SessionLocal()
    categories = db.query(ProductCategory).all()
    cat_names = [c.name for c in categories]
    ai_provider = MockAIProvider()

    print("=" * 80)
    print("                PHASE B: CATEGORY CLASSIFICATION AUDIT               ")
    print("=" * 80)

    # 1. Original 16 Test Cases
    original_tests = [
        ("CAT-01", "Parle-G Biscuit", "Food Products", ["Food Products", "Grocery"]),
        ("CAT-02", "Fortune Basmati Rice 5kg", "Food Products", ["Food Products", "Grocery"]),
        ("CAT-03", "Tata Tea Gold 1kg", "Beverages", ["Beverages", "Food Products"]),
        ("CAT-04", "Nivea Soft Moisturising Cream", "Cosmetics", ["Cosmetics", "Personal Care"]),
        ("CAT-05", "Dove Shampoo 650ml", "Personal Care", ["Personal Care", "Cosmetics"]),
        ("CAT-06", "Samsung Galaxy Smartphone", "Mobile Phones", ["Mobile Phones", "Electronics"]),
        ("CAT-07", "ASUS Vivobook Laptop", "Electronics", ["Electronics"]),
        ("CAT-08", "Puma Men's Cotton T-Shirt", "Clothing", ["Clothing"]),
        ("CAT-09", "Men's Leather Running Shoes", "Footwear", ["Footwear"]),
        ("CAT-10", "Wooden Dining Table Set", "Furniture", ["Furniture"]),
        ("CAT-11", "Bajaj Mixer Grinder", "Kitchen Appliances", ["Kitchen Appliances"]),
        ("CAT-12", "LG Double Door Refrigerator", "Home Appliances", ["Home Appliances"]),
        ("CAT-13", "Dettol Liquid Handwash", "Personal Care", ["Personal Care", "Cleaning Products"]),
        ("CAT-14", "Whey Protein", "Health Supplements", ["Health Supplements", "Food Products"]),
        ("CAT-15", "Paracetamol Tablets", "Medicines", ["Medicines"]),
        ("CAT-16", "Pedigree Adult Dog Food", "Pet Products", ["Pet Products", "Food Products"]),
    ]

    print("\n--- 1. Baseline 16 Test Cases Execution ---")
    print(f"{'ID':<7} | {'Product Input':<32} | {'Expected Category':<22} | {'Actual Category':<20} | Status")
    print("-" * 92)

    passed_orig = 0
    for cid, title, expected, allowed in original_tests:
        actual = ai_provider.classify_category(title, title, cat_names)
        is_pass = actual == expected or actual in allowed
        if is_pass:
            passed_orig += 1
        print(f"{cid:<7} | {title:<32} | {expected:<22} | {actual:<20} | {'PASS' if is_pass else 'FAIL'}")

    acc_orig = (passed_orig / len(original_tests)) * 100
    print(f"\n16-Test Category Accuracy: {passed_orig} / {len(original_tests)} ({acc_orig:.1f}%)")

    # 2. Unseen Products Generalization Test Cases
    unseen_tests = [
        ("UNSEEN-01", "Britannia Good Day Butter Biscuits 600g", "Food Products", ["Food Products", "Grocery"]),
        ("UNSEEN-02", "Aashirvaad Whole Wheat Atta 10kg", "Grocery", ["Grocery", "Food Products"]),
        ("UNSEEN-03", "Nestle Maggi 2-Minute Masala Noodles 420g", "Food Products", ["Food Products", "Grocery"]),
        ("UNSEEN-04", "HP Pavilion 15 Intel Core i7 16GB RAM SSD", "Electronics", ["Electronics"]),
        ("UNSEEN-05", "OnePlus 12 5G Smartphone 256GB", "Mobile Phones", ["Mobile Phones", "Electronics"]),
        ("UNSEEN-06", "Sony WH-1000XM5 Wireless Noise Cancelling Headphones", "Electronics", ["Electronics"]),
        ("UNSEEN-07", "Levi's Men's 511 Slim Fit Stretchable Denim Jeans", "Clothing", ["Clothing"]),
        ("UNSEEN-08", "Allen Solly Men's Cotton Formal Shirt", "Clothing", ["Clothing"]),
        ("UNSEEN-09", "Himalaya Purifying Neem Face Wash 150ml", "Personal Care", ["Personal Care", "Cosmetics"]),
        ("UNSEEN-10", "Vaseline Intensive Care Cocoa Glow Body Lotion 400ml", "Personal Care", ["Personal Care", "Cosmetics"]),
        ("UNSEEN-11", "Philips HD9252/90 Digital Air Fryer 4.1L 1400W", "Kitchen Appliances", ["Kitchen Appliances"]),
        ("UNSEEN-12", "Godrej 190L 4 Star Direct Cool Single Door Refrigerator", "Home Appliances", ["Home Appliances"]),
        ("UNSEEN-13", "MuscleBlaze Biozyme Performance Whey Protein Powder 2kg", "Health Supplements", ["Health Supplements", "Food Products"]),
        ("UNSEEN-14", "Crocin Pain Relief Tablets 650mg", "Medicines", ["Medicines"]),
    ]

    print("\n--- 2. Unseen Products Generalization Test Cases ---")
    print(f"{'ID':<10} | {'Unseen Product Title':<50} | {'Expected':<20} | {'Actual':<20} | Status")
    print("-" * 110)

    passed_unseen = 0
    for uid, title, expected, allowed in unseen_tests:
        actual = ai_provider.classify_category(title, title, cat_names)
        is_pass = actual == expected or actual in allowed
        if is_pass:
            passed_unseen += 1
        print(f"{uid:<10} | {title[:48]:<50} | {expected:<20} | {actual:<20} | {'PASS' if is_pass else 'FAIL'}")

    acc_unseen = (passed_unseen / len(unseen_tests)) * 100
    print(f"\nUnseen Products Accuracy: {passed_unseen} / {len(unseen_tests)} ({acc_unseen:.1f}%)")

    db.close()

if __name__ == "__main__":
    execute_phase_b()
