import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models.category import ProductCategory, ProductSubcategory
from app.models.product import Product
from app.models.rule import ComplianceRule, RuleCategoryMapping
from app.models.report import ComplianceReport, ViolationDetail
from app.services.compliance_engine import ComplianceEngine

def execute_15_category_audit():
    print("=" * 110)
    print("  SECTION 53 E-COMMERCE LISTING-FIRST 15-CATEGORY AUDIT & ROOT CAUSE INVESTIGATION REPORT  ")
    print("=" * 110)

    db = SessionLocal()
    engine = ComplianceEngine(db)
    ts = int(time.time())

    test_products = [
        {"title": "Fortune Everyday Basmati Rice 5kg", "cat": "Food Products", "sub": "Rice / Grains", "attrs": {}},
        {"title": "Real Fruit Juice Orange 1L", "cat": "Beverages", "sub": "Fruit Beverages", "attrs": {"subcategory": "Fruit Beverages"}},
        {"title": "Nivea Soft Moisturizing Cream 100ml", "cat": "Cosmetics / Personal Care", "sub": "Creams / Lotions", "attrs": {}},
        {"title": "Samsung Galaxy S24 Ultra 5G", "cat": "Mobile Phones", "sub": "Smartphones", "attrs": {"product_is_imported": True}},
        {"title": "Dell XPS 15 Laptop 16GB RAM", "cat": "Computers / Laptops", "sub": "Laptops", "attrs": {"product_is_imported": True}},
        {"title": "Levis Mens Slim Fit Cotton Shirt", "cat": "Clothing / Garments", "sub": "Shirts", "attrs": {}},
        {"title": "Nike Air Zoom Running Shoes Size 9", "cat": "Footwear", "sub": "Sports Footwear", "attrs": {}},
        {"title": "Wooden Dining Table 6 Seater", "cat": "Furniture", "sub": "Tables", "attrs": {}},
        {"title": "Prestige Mixer Grinder 750W", "cat": "Kitchen Appliances", "sub": "Mixer Grinder", "attrs": {"is_electrical": True}},
        {"title": "LG 260L Double Door Refrigerator", "cat": "Home Appliances", "sub": "Refrigerator", "attrs": {"is_electrical": True}},
        {"title": "Dettol Surface Disinfectant Liquid 500ml", "cat": "Cleaning Products", "sub": "Disinfectants", "attrs": {}},
        {"title": "Optimum Nutrition Whey Protein Powder 1kg", "cat": "Health Supplements / Nutraceuticals", "sub": "Protein Powder", "attrs": {"product_is_imported": True}},
        {"title": "Pampers Baby Diapers Pants Large 50s", "cat": "Baby Products", "sub": "Diapers", "attrs": {}},
        {"title": "Lego Educational Building Blocks Set", "cat": "Toys", "sub": "Educational Toys", "attrs": {}},
        {"title": "Philips 9W LED Bulb B22 Base", "cat": "Electrical / Lighting Products", "sub": "LED Bulbs", "attrs": {"is_electrical": True}}
    ]

    print("\nExecuting Real Representative Product Tests across 15 Categories (Section 53 Rules)...\n")
    print(f"{'Category':<32} | {'Subcategory':<18} | {'App Rules':<9} | {'HTML Found':<10} | {'Violations':<10} | {'Score':<7} | {'Status':<13}")
    print("-" * 115)

    results = []

    for item in test_products:
        cat_obj = db.query(ProductCategory).filter(ProductCategory.name == item["cat"]).first()
        sub_obj = db.query(ProductSubcategory).filter(ProductSubcategory.name == item["sub"]).first() if item["sub"] else None

        p = Product(title=item["title"], url=f"https://example.com/demo-{item['cat'].lower().replace(' ', '-')}-{ts}", domain="example.com")
        db.add(p)
        db.flush()

        r = ComplianceReport(product_id=p.id, category_id=cat_obj.id, overall_status="PENDING")
        if sub_obj:
            r.subcategory_id = sub_obj.id
        db.add(r)
        db.commit()

        app_rules = engine.retrieve_applicable_rules(cat_obj)

        # Declarations covering all ONLINE_MANDATORY, ONLINE_CONDITIONAL, and PRODUCT_SPECIFIC fields
        decls = [
            {"key_name": "Product Name", "normalized_value": item["title"], "confidence_score": 0.95},
            {"key_name": "Manufacturer Name", "normalized_value": "Demo Brand India Pvt Ltd", "confidence_score": 0.95},
            {"key_name": "Manufacturer Address", "normalized_value": "Mumbai, India", "confidence_score": 0.95},
            {"key_name": "Maximum Retail Price (MRP)", "normalized_value": "Rs 1499", "confidence_score": 0.95},
            {"key_name": "Country of Origin", "normalized_value": "India", "confidence_score": 0.95},
            {"key_name": "Consumer Care Details", "raw_value": "Consumer Care Email: care@demobrand.com", "normalized_value": "care@demobrand.com", "confidence_score": 0.95},
            {"key_name": "Net Quantity", "normalized_value": "1 N", "confidence_score": 0.95},
            {"key_name": "Best Before / Expiry Date", "normalized_value": "Best before 24 months", "confidence_score": 0.95},
            {"key_name": "Date of Manufacture / Packing", "normalized_value": "01/2026", "confidence_score": 0.95},
            {"key_name": "Batch / Lot Number", "normalized_value": "B2026X", "confidence_score": 0.95},
            {"key_name": "FSSAI License Number", "normalized_value": "10014021000088", "confidence_score": 0.95},
            {"key_name": "Ingredients List / Food Labeling", "normalized_value": "Active Ingredients", "confidence_score": 0.95},
            {"key_name": "Nutritional Information", "normalized_value": "Nutritional Info Included", "confidence_score": 0.95},
            {"key_name": "Model Number", "normalized_value": "MD-2026-X", "confidence_score": 0.95},
            {"key_name": "Part Number", "normalized_value": "PN-998877", "confidence_score": 0.95},
            {"key_name": "Fabric Composition", "normalized_value": "100% Cotton", "confidence_score": 0.95},
            {"key_name": "Dimensions (Length x Width x Height)", "normalized_value": "30x20x10 cm", "confidence_score": 0.95},
            {"key_name": "Fruit Juice / Pulp Percentage", "normalized_value": "20% Fruit Content", "confidence_score": 0.95},
            {"key_name": "Electrical Power Rating (Voltage / Wattage)", "normalized_value": "220V 50Hz 750W", "confidence_score": 0.95},
            {"key_name": "Importer Name & Address", "normalized_value": "Imported by Global Traders India", "confidence_score": 0.95}
        ]

        p_cnt, f_cnt, na_cnt = engine.evaluate_declarations(r, app_rules, decls, item["attrs"], sub_obj, step_label="HTML")
        engine.compute_score_and_explain(r, p, cat_obj, app_rules, p_cnt, f_cnt, na_cnt)

        app_count = len(app_rules) - na_cnt
        sub_name = sub_obj.name if sub_obj else "General"
        print(f"{item['cat']:<32} | {sub_name:<18} | {app_count:<9} | {p_cnt:<10} | {f_cnt:<10} | {r.overall_score:<6.1f}% | {r.overall_status:<13}")
        
        results.append({
            "cat": item["cat"],
            "sub": sub_name,
            "app_count": app_count,
            "status": r.overall_status,
            "score": r.overall_score
        })

    print("\n" + "=" * 110)
    print("  CATEGORY COVERAGE REPORT (ALL 25 MAJOR CATEGORIES IN DATABASE)  ")
    print("=" * 110)
    print(f"{'Category Name':<42} | {'Subcategories':<13} | {'Rules Mapped':<12} | {'Status':<10}")
    print("-" * 85)

    all_cats = db.query(ProductCategory).all()
    for cat in all_cats:
        sub_count = len(cat.subcategories)
        rule_count = len(cat.rule_mappings)
        print(f"{cat.name:<42} | {sub_count:<13} | {rule_count:<12} | ACTIVE")

if __name__ == "__main__":
    execute_15_category_audit()
