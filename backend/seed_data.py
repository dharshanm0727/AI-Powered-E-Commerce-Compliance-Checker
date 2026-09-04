from sqlalchemy.orm import Session
from app.core.database import engine, SessionLocal, Base
from app.core.security import get_password_hash
from app.models.user import User
from app.models.category import ProductCategory, ProductSubcategory
from app.models.rule import ComplianceRule, RuleCategoryMapping

def seed_database():
    """
    Idempotent database seeder for Legal Metrology (Packaged Commodities) Rules,
    supporting 25 major categories, subcategories, dynamic conditional rules,
    e-commerce listing-first rule classifications (Section 53), evidence sources,
    and regulatory source metadata.
    """
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        pass

    db = SessionLocal()

    try:
        # Check if schema matches current models, recreate if outdated local SQLite
        try:
            db.query(ComplianceRule).first()
        except Exception:
            db.close()
            Base.metadata.drop_all(bind=engine)
            Base.metadata.create_all(bind=engine)
            db = SessionLocal()

        # 1. Admin & Default Auditor Users (Idempotent)
        admin = db.query(User).filter(User.email == "admin@compliance.com").first()
        if not admin:
            admin = User(
                email="admin@compliance.com",
                full_name="Admin Compliance Officer",
                hashed_password=get_password_hash("admin123"),
                role="admin",
                is_active=True
            )
            db.add(admin)

        user = db.query(User).filter(User.email == "user@compliance.com").first()
        if not user:
            user = User(
                email="user@compliance.com",
                full_name="Standard Auditor",
                hashed_password=get_password_hash("user123"),
                role="user",
                is_active=True
            )
            db.add(user)
        db.commit()

        # 2. Complete List of 25 Major Categories & Subcategories
        categories_structure = [
            {
                "name": "Food Products",
                "description": "Packaged Food, Snacks, Biscuits, Grains, Edible Oils, Cereals",
                "subcategories": ["Rice / Grains", "Biscuits", "Snacks", "Dairy Products", "Processed Foods", "Packaged Foods", "Health/Special Dietary Food", "Organic Food", "Fortified Food"]
            },
            {
                "name": "Beverages",
                "description": "Packaged Water, Juices, Soft Drinks, Tea, Coffee, Energy Drinks",
                "subcategories": ["Tea", "Coffee", "Soft Drinks", "Fruit Beverages", "Energy Drinks", "Packaged Water", "Other Beverages"]
            },
            {
                "name": "Cosmetics / Personal Care",
                "description": "Skincare, Haircare, Lipsticks, Serums, Lotions, Makeup, Hygiene",
                "subcategories": ["Shampoo", "Skin Care", "Hair Care", "Soap", "Oral Care", "Deodorants", "Creams / Lotions"]
            },
            {
                "name": "Electronics",
                "description": "Televisions, Audio Devices, Cameras, Electronic Accessories",
                "subcategories": ["Televisions", "Audio Devices", "Cameras", "Accessories", "Other Consumer Electronics"]
            },
            {
                "name": "Mobile Phones",
                "description": "Smartphones, Feature Phones, Mobile Accessories",
                "subcategories": ["Smartphones", "Feature Phones", "Chargers", "Mobile Accessories"]
            },
            {
                "name": "Computers / Laptops",
                "description": "Desktops, Laptops, Monitors, Storage Devices, PC Peripherals",
                "subcategories": ["Laptops", "Desktops", "Monitors", "Storage Devices", "PC Accessories"]
            },
            {
                "name": "Clothing / Garments",
                "description": "Men, Women, Kids Apparel, Textiles, Shirts, Denim, Dresses",
                "subcategories": ["T-Shirts", "Shirts", "Trousers", "Dresses", "Innerwear", "Children's Clothing"]
            },
            {
                "name": "Footwear",
                "description": "Shoes, Boots, Sandals, Slippers, Athletic Footwear",
                "subcategories": ["Shoes", "Sandals", "Slippers", "Sports Footwear"]
            },
            {
                "name": "Furniture",
                "description": "Beds, Tables, Chairs, Sofas, Wardrobes, Office Desks",
                "subcategories": ["Beds", "Tables", "Chairs", "Sofas", "Wardrobes", "Desks"]
            },
            {
                "name": "Kitchen Appliances",
                "description": "Mixer Grinders, Juicers, Induction Cooktops, Ovens, Kettles",
                "subcategories": ["Mixer Grinder", "Microwave", "Induction Stove", "Electric Kettle", "Toaster"]
            },
            {
                "name": "Home Appliances",
                "description": "Refrigerators, Washing Machines, Air Conditioners, Air Coolers",
                "subcategories": ["Refrigerator", "Washing Machine", "Air Conditioner", "Water Heater", "Other Appliances"]
            },
            {
                "name": "Cleaning Products",
                "description": "Detergents, Surface Cleaners, Disinfectants, Soaps",
                "subcategories": ["Laundry Detergent", "Dishwash", "Surface Cleaners", "Disinfectants"]
            },
            {
                "name": "Health Supplements / Nutraceuticals",
                "description": "Protein Powders, Vitamins, Health Drinks, Dietary Supplements",
                "subcategories": ["Protein Powder", "Vitamins & Minerals", "Dietary Supplements", "Ayurvedic Supplements"]
            },
            {
                "name": "Medicines",
                "description": "Pharmaceutical Formulations, Syrups, Tablets, Ointments",
                "subcategories": ["Tablets / Capsules", "Syrups", "Ointments / Creams", "Injections"]
            },
            {
                "name": "Baby Products",
                "description": "Diapers, Baby Wipes, Strollers, Baby Skincare",
                "subcategories": ["Diapers", "Wipes", "Baby Skincare", "Strollers & Gears"]
            },
            {
                "name": "Infant Foods",
                "description": "Infant Formula, Baby Cereal, Follow-up Formula",
                "subcategories": ["Infant Formula", "Infant Cereal", "Follow-up Formula"]
            },
            {
                "name": "Pet Products / Pet Food",
                "description": "Dog Food, Cat Food, Pet Grooming, Pet Toys",
                "subcategories": ["Dog Food", "Cat Food", "Pet Grooming", "Pet Accessories"]
            },
            {
                "name": "Stationery / School Supplies",
                "description": "Pens, Notebooks, Office Supplies, Art Materials, School Bags",
                "subcategories": ["Notebooks", "Pens & Pencils", "Art Supplies", "Files & Folders", "School Bags"]
            },
            {
                "name": "Toys",
                "description": "Action Figures, Puzzles, Board Games, Educational Toys",
                "subcategories": ["Educational Toys", "Electronic Toys", "Infant Toys", "Outdoor Toys"]
            },
            {
                "name": "Sports & Fitness Products",
                "description": "Fitness Gear, Balls, Rackets, Gym Accessories",
                "subcategories": ["Fitness Equipment", "Sports Accessories", "Exercise Equipment"]
            },
            {
                "name": "Automotive Accessories",
                "description": "Car Accessories, Engine Oil, Spare Parts, Helmets",
                "subcategories": ["Car Accessories", "Bike Accessories", "Helmets & Safety", "Lubricants"]
            },
            {
                "name": "Hardware / Tools",
                "description": "Screwdrivers, Power Tools, Hand Tools, Fasteners",
                "subcategories": ["Hand Tools", "Power Tools", "Fasteners", "Measuring Tools"]
            },
            {
                "name": "Electrical / Lighting Products",
                "description": "LED Bulbs, Switches, Wires, Lighting Fixtures",
                "subcategories": ["LED Bulbs", "Lamps", "Switches", "Wires & Cables"]
            },
            {
                "name": "Watches / Accessories / Jewellery",
                "description": "Wristwatches, Fine Jewellery, Fashion Accessories",
                "subcategories": ["Wristwatches", "Fine Jewellery", "Fashion Accessories"]
            },
            {
                "name": "Miscellaneous / General Packaged Commodities",
                "description": "Fallback General Packaged Commodities requiring standard metrology declarations",
                "subcategories": ["General Commodities", "Unclassified Packaged Goods"]
            }
        ]

        cat_map = {}
        for cdata in categories_structure:
            cname = cdata["name"]
            existing_cat = db.query(ProductCategory).filter(ProductCategory.name == cname).first()
            if not existing_cat:
                existing_cat = ProductCategory(name=cname, description=cdata["description"])
                db.add(existing_cat)
                db.commit()
                db.refresh(existing_cat)
            else:
                existing_cat.description = cdata["description"]
                db.commit()
            cat_map[cname] = existing_cat

            # Seed subcategories
            for sub_name in cdata["subcategories"]:
                existing_sub = db.query(ProductSubcategory).filter(
                    ProductSubcategory.category_id == existing_cat.id,
                    ProductSubcategory.name == sub_name
                ).first()
                if not existing_sub:
                    db.add(ProductSubcategory(category_id=existing_cat.id, name=sub_name))
            db.commit()

        # 3. Rules Database Definition with Section 53 E-Commerce Rule Classifications
        rules_data = [
            # ONLINE_MANDATORY Legal Metrology E-Commerce Declarations
            {
                "rule_code": "LM-CORE-01",
                "declaration_name": "Product Name",
                "description": "Generic or common name of the commodity contained in the package",
                "mandatory_fields": "Product Name, Generic Name, Title, Item Name, Commodity Name",
                "enforcement_level": "strict",
                "rule_type": "ONLINE_MANDATORY",
                "applicability_type": "MANDATORY",
                "evidence_source": "HTML_OR_IMAGE",
                "source_name": "Legal Metrology (Packaged Commodities) Rules, 2011",
                "regulation_name": "PCR 2011 Rule 6",
                "source_reference": "Rule 6(1)(b)",
                "verification_status": "VERIFIED",
                "legal_reference": "Rule 6(1)(b), Legal Metrology (Packaged Commodities) Rules, 2011",
                "version": "2024.1"
            },
            {
                "rule_code": "LM-CORE-02",
                "declaration_name": "Manufacturer Name",
                "description": "Name of the manufacturer or packer of the package",
                "mandatory_fields": "Manufactured by, Manufacturer Name, Mfd by, Packed by, Packer",
                "enforcement_level": "strict",
                "rule_type": "ONLINE_MANDATORY",
                "applicability_type": "MANDATORY",
                "evidence_source": "HTML_OR_IMAGE",
                "source_name": "Legal Metrology (Packaged Commodities) Rules, 2011",
                "regulation_name": "PCR 2011 Rule 6",
                "source_reference": "Rule 6(1)(a)",
                "verification_status": "VERIFIED",
                "legal_reference": "Rule 6(1)(a), Legal Metrology (Packaged Commodities) Rules, 2011",
                "version": "2024.1"
            },
            {
                "rule_code": "LM-CORE-03",
                "declaration_name": "Manufacturer Address",
                "description": "Complete postal address of the manufacturer or packer",
                "mandatory_fields": "Manufacturer Address, Address, Factory Address, Registered Office",
                "enforcement_level": "strict",
                "rule_type": "ONLINE_MANDATORY",
                "applicability_type": "MANDATORY",
                "evidence_source": "HTML_OR_IMAGE",
                "source_name": "Legal Metrology (Packaged Commodities) Rules, 2011",
                "regulation_name": "PCR 2011 Rule 6",
                "source_reference": "Rule 6(1)(a)",
                "verification_status": "VERIFIED",
                "legal_reference": "Rule 6(1)(a), Legal Metrology (Packaged Commodities) Rules, 2011",
                "version": "2024.1"
            },
            {
                "rule_code": "LM-CORE-04",
                "declaration_name": "Maximum Retail Price (MRP)",
                "description": "Maximum Retail Price inclusive of all taxes in Indian Rupees",
                "mandatory_fields": "MRP, Price, Maximum Retail Price, Inclusive of all taxes, ₹, Rs",
                "enforcement_level": "strict",
                "rule_type": "ONLINE_MANDATORY",
                "applicability_type": "MANDATORY",
                "evidence_source": "HTML_OR_IMAGE",
                "source_name": "Legal Metrology (Packaged Commodities) Rules, 2011",
                "regulation_name": "PCR 2011 Rule 6",
                "source_reference": "Rule 6(1)(e)",
                "verification_status": "VERIFIED",
                "legal_reference": "Rule 6(1)(e), Legal Metrology (Packaged Commodities) Rules, 2011",
                "version": "2024.1"
            },
            {
                "rule_code": "LM-CORE-05",
                "declaration_name": "Country of Origin",
                "description": "Country of origin where the product was manufactured or produced",
                "mandatory_fields": "Country of Origin, Made in, Origin, Country of Manufacture",
                "enforcement_level": "strict",
                "rule_type": "ONLINE_MANDATORY",
                "applicability_type": "MANDATORY",
                "evidence_source": "HTML_OR_IMAGE",
                "source_name": "Legal Metrology (Packaged Commodities) Amendment Rules, 2020",
                "regulation_name": "PCR 2020 Amendment",
                "source_reference": "Rule 6(1)(aa)",
                "verification_status": "VERIFIED",
                "legal_reference": "Rule 6(1)(aa), Legal Metrology (Packaged Commodities) Amendment Rules, 2020",
                "version": "2024.1"
            },
            {
                "rule_code": "LM-CORE-06",
                "declaration_name": "Consumer Care Details",
                "description": "Name, address, telephone number and email address of person/office for consumer complaints",
                "mandatory_fields": "Consumer Care, Customer Care, Consumer Helpline, Helpline, Email, Phone, Toll Free, Contact Us",
                "enforcement_level": "strict",
                "rule_type": "ONLINE_MANDATORY",
                "applicability_type": "MANDATORY",
                "evidence_source": "HTML_OR_IMAGE",
                "source_name": "Legal Metrology (Packaged Commodities) Rules, 2011",
                "regulation_name": "PCR 2011 Rule 6",
                "source_reference": "Rule 6(1)(g)",
                "verification_status": "VERIFIED",
                "legal_reference": "Rule 6(1)(g), Legal Metrology (Packaged Commodities) Rules, 2011",
                "version": "2024.1"
            },
            {
                "rule_code": "LM-CORE-07",
                "declaration_name": "Net Quantity",
                "description": "Net quantity in standard units of mass, volume, length, area, or number",
                "mandatory_fields": "Net Quantity, Net Weight, Net Vol, Volume, Weight, Qty, Net Qty",
                "enforcement_level": "strict",
                "rule_type": "ONLINE_MANDATORY",
                "applicability_type": "MANDATORY",
                "evidence_source": "HTML_OR_IMAGE",
                "source_name": "Legal Metrology (Packaged Commodities) Rules, 2011",
                "regulation_name": "PCR 2011 Rule 6",
                "source_reference": "Rule 6(1)(c)",
                "verification_status": "VERIFIED",
                "legal_reference": "Rule 6(1)(c), Legal Metrology (Packaged Commodities) Rules, 2011",
                "version": "2024.1"
            },

            # PACKAGE_OR_IMAGE_VERIFICATION Physical Packaging Declarations
            {
                "rule_code": "LM-CORE-08",
                "declaration_name": "Best Before / Expiry Date",
                "description": "Date of expiry or best before period for consumption / package validity",
                "mandatory_fields": "Best Before, Use By, Expiry Date, Exp Date",
                "enforcement_level": "strict",
                "rule_type": "PACKAGE_OR_IMAGE_VERIFICATION",
                "applicability_type": "MANDATORY",
                "evidence_source": "PACKAGE_ONLY",
                "source_name": "Legal Metrology (Packaged Commodities) Rules, 2011",
                "regulation_name": "PCR 2011 Rule 6",
                "source_reference": "Rule 6(1)(d)",
                "verification_status": "VERIFIED",
                "legal_reference": "Rule 6(1)(d), Legal Metrology (Packaged Commodities) Rules, 2011",
                "version": "2024.1"
            },
            {
                "rule_code": "LM-CORE-09",
                "declaration_name": "Date of Manufacture / Packing",
                "description": "Month and year of manufacture or packaging on physical container",
                "mandatory_fields": "Date of Manufacture, Date of Packing, Pkd Date, Mfg Date",
                "enforcement_level": "strict",
                "rule_type": "PACKAGE_OR_IMAGE_VERIFICATION",
                "applicability_type": "MANDATORY",
                "evidence_source": "PACKAGE_ONLY",
                "source_name": "Legal Metrology (Packaged Commodities) Rules, 2011",
                "regulation_name": "PCR 2011 Rule 6",
                "source_reference": "Rule 6(1)(d)",
                "verification_status": "VERIFIED",
                "legal_reference": "Rule 6(1)(d), Legal Metrology (Packaged Commodities) Rules, 2011",
                "version": "2024.1"
            },
            {
                "rule_code": "LM-CORE-10",
                "declaration_name": "Batch / Lot Number",
                "description": "Distinctive batch or lot identification number on physical container",
                "mandatory_fields": "Batch Number, Lot Number, Batch No, B.No",
                "enforcement_level": "strict",
                "rule_type": "PACKAGE_OR_IMAGE_VERIFICATION",
                "applicability_type": "MANDATORY",
                "evidence_source": "PACKAGE_ONLY",
                "source_name": "Legal Metrology (Packaged Commodities) Rules, 2011",
                "regulation_name": "PCR 2011 Rule 6",
                "source_reference": "Rule 6(1)(d)",
                "verification_status": "VERIFIED",
                "legal_reference": "Rule 6(1)(d), Legal Metrology (Packaged Commodities) Rules, 2011",
                "version": "2024.1"
            },

            # PRODUCT_SPECIFIC Additional Declarations
            {
                "rule_code": "LM-ELEC-01",
                "declaration_name": "Model Number",
                "description": "Model identification number for electronic & electrical goods",
                "mandatory_fields": "Model Number, Model Name, Model, Series",
                "enforcement_level": "warning",
                "rule_type": "PRODUCT_SPECIFIC",
                "applicability_type": "MANDATORY",
                "evidence_source": "HTML_OR_IMAGE",
                "source_name": "Advisory for Electronic Commodities",
                "regulation_name": "PCR Electronics Advisory 2022",
                "source_reference": "Rule 6(1)(h)",
                "verification_status": "VERIFIED",
                "legal_reference": "Rule 6(1)(h), Legal Metrology (Packaged Commodities) Rules, 2011",
                "version": "2024.1"
            },
            {
                "rule_code": "LM-ELEC-06",
                "declaration_name": "Part Number",
                "description": "Mandatory Part Number identification for electrical and electronic items",
                "mandatory_fields": "Part Number, Part No, P/N, Part #, Item Part Number",
                "enforcement_level": "strict",
                "rule_type": "PRODUCT_SPECIFIC",
                "applicability_type": "MANDATORY",
                "evidence_source": "HTML_OR_IMAGE",
                "source_name": "Advisory for Electronic Commodities",
                "regulation_name": "PCR Electronics Advisory 2022",
                "source_reference": "Rule 6(1)(h)",
                "verification_status": "VERIFIED",
                "legal_reference": "Rule 6(1)(h) Read with Advisory for Electronic Commodities, 2022",
                "version": "2024.1"
            },
            {
                "rule_code": "LM-DIM-01",
                "declaration_name": "Dimensions (Length x Width x Height)",
                "description": "Dimensions of commodity where relevance applies (clothing, furniture, appliances)",
                "mandatory_fields": "Dimensions, Size, Height, Width, Length, Chest, Waist, Measurement",
                "enforcement_level": "strict",
                "rule_type": "PRODUCT_SPECIFIC",
                "applicability_type": "MANDATORY",
                "evidence_source": "HTML_OR_IMAGE",
                "source_name": "Legal Metrology (Packaged Commodities) Rules, 2011",
                "regulation_name": "PCR 2011 Rule 6",
                "source_reference": "Rule 6(1)(f)",
                "verification_status": "VERIFIED",
                "legal_reference": "Rule 6(1)(f), Legal Metrology (Packaged Commodities) Rules, 2011",
                "version": "2024.1"
            },

            # Food Product Specific Rules (FSSAI)
            {
                "rule_code": "LM-FOOD-01",
                "declaration_name": "FSSAI License Number",
                "description": "Mandatory 14-digit FSSAI food safety license logo and number",
                "mandatory_fields": "FSSAI, Lic No, License Number, Food Lic",
                "enforcement_level": "strict",
                "rule_type": "PRODUCT_SPECIFIC",
                "applicability_type": "MANDATORY",
                "evidence_source": "HTML_OR_IMAGE",
                "source_name": "Food Safety and Standards Regulations",
                "regulation_name": "FSSAI Labelling Regulations 2020",
                "source_reference": "Reg 5(1)",
                "verification_status": "VERIFIED",
                "legal_reference": "Food Safety and Standards (Labelling and Display) Regulations, 2020",
                "version": "2024.1"
            },
            {
                "rule_code": "LM-FOOD-03",
                "declaration_name": "Ingredients List / Food Labeling",
                "description": "List of ingredients in descending order of weight or volume",
                "mandatory_fields": "Ingredients, Composition, Food Labeling",
                "enforcement_level": "strict",
                "rule_type": "PRODUCT_SPECIFIC",
                "applicability_type": "MANDATORY",
                "evidence_source": "HTML_OR_IMAGE",
                "source_name": "Food Safety and Standards Regulations",
                "regulation_name": "FSSAI Labelling Regulations 2020",
                "source_reference": "Reg 5(2)",
                "verification_status": "VERIFIED",
                "legal_reference": "FSSAI Packaging & Labelling Regulations, 2020",
                "version": "2024.1"
            },
            {
                "rule_code": "LM-FOOD-04",
                "declaration_name": "Nutritional Information",
                "description": "Nutritional breakdown per 100g or per serve",
                "mandatory_fields": "Nutritional Information, Energy, Protein, Carbohydrates, Fat, Calories",
                "enforcement_level": "strict",
                "rule_type": "PRODUCT_SPECIFIC",
                "applicability_type": "MANDATORY",
                "evidence_source": "HTML_OR_IMAGE",
                "source_name": "Food Safety and Standards Regulations",
                "regulation_name": "FSSAI Labelling Regulations 2020",
                "source_reference": "Reg 5(3)",
                "verification_status": "VERIFIED",
                "legal_reference": "FSSAI Labelling & Display Regulations, 2020",
                "version": "2024.1"
            },

            # Cosmetics Rules
            {
                "rule_code": "LM-COSM-01",
                "declaration_name": "Batch Number",
                "description": "Distinctive Batch or Lot Number assigned under Drugs & Cosmetics Rules",
                "mandatory_fields": "Batch Number, Lot Number, Batch No, B.No",
                "enforcement_level": "strict",
                "rule_type": "PACKAGE_OR_IMAGE_VERIFICATION",
                "applicability_type": "MANDATORY",
                "evidence_source": "PACKAGE_ONLY",
                "source_name": "Drugs and Cosmetics Rules, 1945",
                "regulation_name": "Cosmetics Rules 2020",
                "source_reference": "Rule 148",
                "verification_status": "VERIFIED",
                "legal_reference": "Rule 148 of Drugs and Cosmetics Rules, 1945 read with PCR Rule 6",
                "version": "2024.1"
            },

            # Textiles Rules
            {
                "rule_code": "LM-TEX-01",
                "declaration_name": "Fabric Composition",
                "description": "Fiber or material composition declaration for garments and textiles",
                "mandatory_fields": "Fabric, Fiber Content, Cotton, Polyester, Material",
                "enforcement_level": "strict",
                "rule_type": "PRODUCT_SPECIFIC",
                "applicability_type": "MANDATORY",
                "evidence_source": "HTML_OR_IMAGE",
                "source_name": "Legal Metrology Textiles Schedule",
                "regulation_name": "PCR Textiles Schedule",
                "source_reference": "Rule 6(1)(f)",
                "verification_status": "VERIFIED",
                "legal_reference": "Legal Metrology (Packaged Commodities) Rules, 2011 - Textiles Schedule",
                "version": "2024.1"
            },

            # Medicines Rules
            {
                "rule_code": "LM-MED-01",
                "declaration_name": "Manufacturing License Number",
                "description": "Drug manufacturing license number issued by State/Central Licensing Authority",
                "mandatory_fields": "Mfg Lic No, License Number",
                "enforcement_level": "strict",
                "rule_type": "PACKAGE_OR_IMAGE_VERIFICATION",
                "applicability_type": "MANDATORY",
                "evidence_source": "PACKAGE_ONLY",
                "source_name": "Drugs & Cosmetics Act, 1940",
                "regulation_name": "Drugs Rules 1945",
                "source_reference": "Rule 96",
                "verification_status": "VERIFIED",
                "legal_reference": "Drugs & Cosmetics Act, 1940 read with Legal Metrology Exemption Guidelines",
                "version": "2024.1"
            },

            # ONLINE_CONDITIONAL Rules (Evaluated dynamically against product attributes)
            {
                "rule_code": "LM-COND-01",
                "declaration_name": "Fruit Juice / Pulp Percentage",
                "description": "Mandatory fruit content percentage declaration for fruit beverages and juices",
                "mandatory_fields": "Fruit Juice, Juice Percentage, Pulp %, Fruit Content",
                "enforcement_level": "strict",
                "rule_type": "ONLINE_CONDITIONAL",
                "applicability_type": "CONDITIONAL",
                "evidence_source": "HTML_OR_IMAGE",
                "applicability_condition_json": {"attribute": "subcategory", "operator": "equals", "value": "Fruit Beverages"},
                "source_name": "FSSAI Beverages Labelling Regulations",
                "regulation_name": "FSSAI Reg 2.3",
                "source_reference": "Clause 2.3.10",
                "verification_status": "VERIFIED",
                "legal_reference": "FSSAI (Food Products Standards and Food Additives) Regulations",
                "version": "2024.1"
            },
            {
                "rule_code": "LM-COND-02",
                "declaration_name": "Fortification Declaration & Logo",
                "description": "Mandatory +F logo and fortification declaration for fortified foods",
                "mandatory_fields": "Fortified, +F, Fortification, Enriched with",
                "enforcement_level": "strict",
                "rule_type": "ONLINE_CONDITIONAL",
                "applicability_type": "CONDITIONAL",
                "evidence_source": "HTML_OR_IMAGE",
                "applicability_condition_json": {"attribute": "is_fortified", "operator": "equals", "value": True},
                "source_name": "FSSAI Fortification of Foods Regulations, 2018",
                "regulation_name": "FSSAI Fortification 2018",
                "source_reference": "Reg 7",
                "verification_status": "VERIFIED",
                "legal_reference": "FSSAI (Fortification of Foods) Regulations, 2018",
                "version": "2024.1"
            },
            {
                "rule_code": "LM-COND-03",
                "declaration_name": "Organic Food Certification & Logo",
                "description": "Jaivik Bharat logo and organic certification number for organic produce",
                "mandatory_fields": "Organic, Jaivik Bharat, Certified Organic",
                "enforcement_level": "strict",
                "rule_type": "ONLINE_CONDITIONAL",
                "applicability_type": "CONDITIONAL",
                "evidence_source": "HTML_OR_IMAGE",
                "applicability_condition_json": {"attribute": "is_organic", "operator": "equals", "value": True},
                "source_name": "FSSAI Organic Foods Regulations, 2017",
                "regulation_name": "FSSAI Organic Reg 2017",
                "source_reference": "Reg 5",
                "verification_status": "VERIFIED",
                "legal_reference": "FSSAI (Organic Foods) Regulations, 2017",
                "version": "2024.1"
            },
            {
                "rule_code": "LM-COND-04",
                "declaration_name": "Infant Food Safety Notice",
                "description": "Mandatory Mother's Milk is Best for Baby warning notice on infant food",
                "mandatory_fields": "Mother's Milk is Best, Infant Notice, Infant Warning",
                "enforcement_level": "strict",
                "rule_type": "ONLINE_CONDITIONAL",
                "applicability_type": "CONDITIONAL",
                "evidence_source": "HTML_OR_IMAGE",
                "applicability_condition_json": {"attribute": "subcategory", "operator": "equals", "value": "Infant Formula"},
                "source_name": "IMS Act read with FSSAI Regulations",
                "regulation_name": "Infant Milk Substitutes Act, 1992",
                "source_reference": "Sec 6",
                "verification_status": "VERIFIED",
                "legal_reference": "Infant Milk Substitutes, Feeding Bottles and Infant Foods Act, 1992",
                "version": "2024.1"
            },
            {
                "rule_code": "LM-COND-05",
                "declaration_name": "Importer Name & Address",
                "description": "Mandatory Indian importer details for imported packaged goods",
                "mandatory_fields": "Imported by, Importer Name, Importer Address",
                "enforcement_level": "strict",
                "rule_type": "ONLINE_CONDITIONAL",
                "applicability_type": "CONDITIONAL",
                "evidence_source": "HTML_OR_IMAGE",
                "applicability_condition_json": {"attribute": "product_is_imported", "operator": "equals", "value": True},
                "source_name": "Legal Metrology (Packaged Commodities) Rules, 2011",
                "regulation_name": "PCR 2011 Importer Provision",
                "source_reference": "Rule 6(1)(a)",
                "verification_status": "VERIFIED",
                "legal_reference": "Rule 6(1)(a), Legal Metrology (Packaged Commodities) Rules, 2011",
                "version": "2024.1"
            },
            {
                "rule_code": "LM-COND-06",
                "declaration_name": "Electrical Power Rating (Voltage / Wattage)",
                "description": "Operating voltage, power consumption in watts, and frequency rating",
                "mandatory_fields": "Voltage, Wattage, Power Rating, Watts, Volts, Hz",
                "enforcement_level": "strict",
                "rule_type": "ONLINE_CONDITIONAL",
                "applicability_type": "CONDITIONAL",
                "evidence_source": "HTML_OR_IMAGE",
                "applicability_condition_json": {"attribute": "is_electrical", "operator": "equals", "value": True},
                "source_name": "Central Electricity Authority Standards",
                "regulation_name": "CEA Safety Regulations",
                "source_reference": "Reg 12",
                "verification_status": "VERIFIED",
                "legal_reference": "Central Electricity Authority (Measures relating to Safety and Electric Supply) Regulations",
                "version": "2024.1"
            }
        ]

        rule_map = {}
        for rdata in rules_data:
            existing_r = db.query(ComplianceRule).filter(ComplianceRule.rule_code == rdata["rule_code"]).first()
            if not existing_r:
                existing_r = ComplianceRule(**rdata)
                db.add(existing_r)
                db.commit()
                db.refresh(existing_r)
            else:
                for k, v in rdata.items():
                    setattr(existing_r, k, v)
                db.commit()
            rule_map[rdata["rule_code"]] = existing_r

        # Clear existing category mappings to re-apply updated linkages idempotently
        db.query(RuleCategoryMapping).delete()
        db.commit()

        # Core Rule Codes
        core_rules = ["LM-CORE-01", "LM-CORE-02", "LM-CORE-03", "LM-CORE-04", "LM-CORE-05", "LM-CORE-06", "LM-CORE-07", "LM-CORE-08", "LM-CORE-09", "LM-CORE-10"]
        food_core_rules = ["LM-CORE-01", "LM-CORE-02", "LM-CORE-03", "LM-CORE-04", "LM-CORE-05", "LM-CORE-06", "LM-CORE-07", "LM-CORE-10"]

        # Map Category-Wise Rules
        category_specific_rules = {
            "Electronics": core_rules + ["LM-ELEC-01", "LM-ELEC-06", "LM-DIM-01", "LM-COND-05", "LM-COND-06"],
            "Electrical / Lighting Products": core_rules + ["LM-ELEC-01", "LM-ELEC-06", "LM-DIM-01", "LM-COND-06"],
            "Home Appliances": core_rules + ["LM-ELEC-01", "LM-DIM-01", "LM-COND-06"],
            "Kitchen Appliances": core_rules + ["LM-ELEC-01", "LM-DIM-01", "LM-COND-06"],

            "Food Products": food_core_rules + ["LM-FOOD-01", "LM-FOOD-03", "LM-FOOD-04", "LM-COND-02", "LM-COND-03", "LM-COND-04", "LM-COND-05"],
            "Beverages": food_core_rules + ["LM-FOOD-01", "LM-FOOD-03", "LM-FOOD-04", "LM-COND-01", "LM-COND-02", "LM-COND-03", "LM-COND-05"],
            "Infant Foods": food_core_rules + ["LM-FOOD-01", "LM-FOOD-03", "LM-FOOD-04", "LM-COND-04"],
            "Health Supplements / Nutraceuticals": food_core_rules + ["LM-FOOD-01", "LM-FOOD-03", "LM-FOOD-04", "LM-COND-05"],

            "Cosmetics / Personal Care": core_rules + ["LM-COSM-01", "LM-COND-05"],
            "Clothing / Garments": core_rules + ["LM-TEX-01", "LM-DIM-01"],
            "Footwear": core_rules + ["LM-DIM-01"],
            "Medicines": ["LM-CORE-01", "LM-CORE-02", "LM-CORE-04", "LM-MED-01", "LM-COSM-01", "LM-CORE-08", "LM-CORE-09", "LM-CORE-10"]
        }

        # Apply to all 25 categories
        for cat_name, cat_obj in cat_map.items():
            mapped_rcodes = category_specific_rules.get(cat_name, core_rules)
            for rcode in set(mapped_rcodes):
                if rcode in rule_map:
                    rule_obj = rule_map[rcode]
                    db.add(RuleCategoryMapping(category_id=cat_obj.id, rule_id=rule_obj.id, is_required=True))

        db.commit()
        print("Idempotent database seeding completed successfully with Section 53 e-commerce rule classifications!")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
