import httpx
import bs4
import json
import re
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

d2c_candidates = [
    # 1. Food
    {"cat": "Food Products", "name": "True Elements Rolled Oats 1kg", "url": "https://www.true-elements.com/products/rolled-oats-1kg"},
    {"cat": "Food Products", "name": "Slurrp Farm Millet Dosa Mix", "url": "https://slurrpfarm.com/products/spinach-millet-dosa-mix"},
    {"cat": "Food Products", "name": "Conscious Food Organic Basmati Rice", "url": "https://www.consciousfood.com/products/basmati-rice"},
    
    # 2. Beverage
    {"cat": "Beverages", "name": "Sleepy Owl Cold Brew Coffee", "url": "https://sleepyowl.co/products/classic-cold-brew-coffee-packs"},
    {"cat": "Beverages", "name": "Vahdam India Masala Chai Tea", "url": "https://www.vahdam.com/products/india-s-original-masala-chai-tea"},
    {"cat": "Beverages", "name": "Chaayos Desi Chai 250g", "url": "https://chaayos.com/products/desi-chai"},
    
    # 3. Cosmetic
    {"cat": "Cosmetics / Personal Care", "name": "Plum Green Tea Face Wash 100ml", "url": "https://plumgoodness.com/products/green-tea-pore-cleansing-face-wash"},
    {"cat": "Cosmetics / Personal Care", "name": "Minimalist Niacinamide 10% Serum", "url": "https://beminimalist.co/products/niacinamide-10"},
    {"cat": "Cosmetics / Personal Care", "name": "WOW Skin Science Apple Cider Vinegar Shampoo", "url": "https://www.buywow.in/products/apple-cider-vinegar-shampoo"},
    
    # 4. Mobile Phone / Personal Gadgets
    {"cat": "Mobile Phones / Gadgets", "name": "Noise ColorFit Pulse Smartwatch", "url": "https://www.gonoise.com/products/colorfit-pulse-2-max-smartwatch"},
    {"cat": "Mobile Phones / Gadgets", "name": "Portronics 20W Fast Charger", "url": "https://www.portronics.com/products/adapto-20"},
    {"cat": "Electronics", "name": "boAt Airdopes 141 Wireless Earbuds", "url": "https://www.boat-lifestyle.com/products/airdopes-141"},
    
    # 5. Laptop / Computers
    {"cat": "Computers / Laptops", "name": "Portronics Wireless Keyboard Mouse Combo", "url": "https://www.portronics.com/products/key7-combo"},
    {"cat": "Computers / Laptops", "name": "Asus ROG Gaming Mouse", "url": "https://in.store.asus.com/gaming-mouse.html"},
    
    # 6. Clothing
    {"cat": "Clothing / Garments", "name": "Snitch Oxford Slim Fit Shirt", "url": "https://www.snitch.co.in/products/oxford-white-solid-shirt"},
    {"cat": "Clothing / Garments", "name": "Beyoung Mens Plain T-Shirt", "url": "https://www.beyoung.in/solid-black-t-shirt"},
    
    # 7. Footwear
    {"cat": "Footwear", "name": "Neemans Everyday Classic Sneakers", "url": "https://neemans.com/products/everyday-classic-sneakers"},
    {"cat": "Footwear", "name": "Campus Mens Running Shoes", "url": "https://www.campusshoes.com/products/first-running-shoes-for-men"},
    {"cat": "Footwear", "name": "Asian Mens Running Shoes", "url": "https://asianfootwears.com/products/asian-tarzan-11-white-running-shoes-for-men"},
    
    # 8. Home/Kitchen Appliance
    {"cat": "Kitchen Appliances", "name": "Wonderchef Nutri-Blend 400W Mixer Grinder", "url": "https://www.wonderchef.com/products/nutri-blend-400w-mixer-grinder-blender-3-unbreakable-jars"},
    {"cat": "Kitchen Appliances", "name": "Borosil Stainless Steel Electric Kettle 1.5L", "url": "https://myborosil.com/products/rio-electric-kettle-1-5l"},
    {"cat": "Kitchen Appliances", "name": "Agaro Grand 4-Slice Pop-Up Toaster", "url": "https://agarolifestyle.com/products/agaro-grand-4-slice-pop-up-toaster"}
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

print("Running live test on legitimate D2C and verified official brand store product URLs...")
verified = []
rejected = []

for item in d2c_candidates:
    url = item["url"]
    cat = item["cat"]
    name = item["name"]
    try:
        with httpx.Client(headers=headers, follow_redirects=True, timeout=12.0) as client:
            resp = client.get(url)
            status = resp.status_code
            final_url = str(resp.url)
            html = resp.text
            soup = bs4.BeautifulSoup(html, "html.parser")
            
            title = soup.title.string.strip() if soup.title and soup.title.string else ""
            h1 = soup.find("h1").get_text(strip=True) if soup.find("h1") else ""
            
            # Check price/mrp
            price_match = re.search(r'(?:₹|Rs\.?|INR)\s*[\d,]+(?:\.\d+)?', html)
            price = price_match.group(0) if price_match else "Not explicitly parsed"
            
            imgs = [img.get("src") for img in soup.find_all("img") if img.get("src") and not any(x in img.get("src") for x in ["icon", "logo", "svg", "pixel"])]
            
            page_lower = (html[:5000] + title).lower()
            is_not_found = status == 404 or "404" in title or "not found" in (title + h1).lower() or "page not found" in page_lower
            is_blocked = status in [403, 503] or "access denied" in page_lower or "captcha" in page_lower
            
            if status == 200 and not is_not_found and not is_blocked and (h1 or len(title) > 5) and len(imgs) > 0:
                print(f"[VERIFIED] {cat} | {name}")
                print(f"   HTTP: {status} | Canonical URL: {final_url}")
                print(f"   Title: {title[:60]}")
                print(f"   H1: {h1[:60]}")
                print(f"   Price found: {price} | Images: {len(imgs)}\n")
                verified.append({
                    "category": cat,
                    "name": name,
                    "url": final_url,
                    "http": status,
                    "title": title or h1,
                    "images": len(imgs),
                    "price": price
                })
            else:
                reason = "404 Not Found" if is_not_found else ("Access Blocked" if is_blocked else f"HTTP {status} / Incompatible DOM")
                print(f"[REJECTED] {cat} | {name} -> {reason}\n")
                rejected.append({"url": url, "reason": reason})
    except Exception as e:
        print(f"[REJECTED] {cat} | {name} -> Error: {e}\n")
        rejected.append({"url": url, "reason": str(e)})

print(f"\nTotal Verified: {len(verified)} | Total Rejected: {len(rejected)}")
