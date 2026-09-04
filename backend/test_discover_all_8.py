import httpx
import bs4
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

candidates_8 = [
    # 1. Food
    {"cat": "Food Products", "name": "True Elements Rolled Oats 1kg", "url": "https://true-elements.com/products/rolled-oats-1kg"},
    {"cat": "Food Products", "name": "True Elements Daily Protein Cereal", "url": "https://true-elements.com/products/daily-protein-cereal"},
    
    # 2. Beverage
    {"cat": "Beverages", "name": "Vahdam India Masala Chai Tea", "url": "https://www.vahdam.in/products/india-s-original-masala-chai-tea"},
    {"cat": "Beverages", "name": "Vahdam Green Tea", "url": "https://www.vahdam.in/products/chamomile-mint-citrus-green-tea"},
    {"cat": "Beverages", "name": "Sleepy Owl Hazelnut Instant Coffee", "url": "https://sleepyowl.co/products/hazelnut-instant-coffee"},
    
    # 3. Cosmetic
    {"cat": "Cosmetics / Personal Care", "name": "Plum Green Tea Face Wash", "url": "https://plumgoodness.com/products/green-tea-pore-cleansing-face-wash"},
    {"cat": "Cosmetics / Personal Care", "name": "Dot & Key Barrier Repair Face Cream", "url": "https://www.dotandkey.com/products/ceramide-barrier-repair-face-cream"},
    {"cat": "Cosmetics / Personal Care", "name": "mCaffeine Espresso Coffee Face Wash", "url": "https://www.mcaffeine.com/products/espresso-coffee-face-wash"},
    
    # 4. Mobile Phone / Personal Gadgets
    {"cat": "Mobile Phones / Gadgets", "name": "Portronics Adapto 20 20W Charger", "url": "https://www.portronics.com/products/adapto-20"},
    {"cat": "Mobile Phones / Gadgets", "name": "Noise ColorFit Pulse 2 Max Smartwatch", "url": "https://www.gonoise.com/products/colorfit-pulse-2-max-smartwatch"},
    
    # 5. Laptop / Computers
    {"cat": "Computers / Laptops", "name": "Portronics Key7 Wireless Keyboard Mouse Combo", "url": "https://www.portronics.com/products/key7-combo"},
    {"cat": "Computers / Laptops", "name": "Portronics Bubble Wireless Mouse", "url": "https://www.portronics.com/products/bubble-wireless-mouse"},
    {"cat": "Electronics", "name": "boAt Airdopes 141 Wireless Earbuds", "url": "https://www.boat-lifestyle.com/products/airdopes-141"},
    
    # 6. Clothing
    {"cat": "Clothing / Garments", "name": "Beyoung Mens Solid Black T-Shirt", "url": "https://www.beyoung.in/solid-black-t-shirt"},
    {"cat": "Clothing / Garments", "name": "Beyoung Navy Blue Polo T-Shirt", "url": "https://www.beyoung.in/navy-blue-polo-t-shirt"},
    
    # 7. Footwear
    {"cat": "Footwear", "name": "Campus First Mens Running Shoes", "url": "https://www.campusshoes.com/products/first-running-shoes-for-men"},
    {"cat": "Footwear", "name": "Campus Mens Running Shoes Ogs", "url": "https://www.campusshoes.com/products/ogs-running-shoes-for-men-black"},
    {"cat": "Footwear", "name": "Asian Shoes Tarzan-11 Running Shoes", "url": "https://asianfootwears.com/products/asian-tarzan-11-white-running-shoes-for-men"},
    
    # 8. Home/Kitchen Appliance
    {"cat": "Kitchen Appliances", "name": "Borosil Rio Electric Kettle 1.5L", "url": "https://myborosil.com/products/rio-electric-kettle-1-5l"},
    {"cat": "Kitchen Appliances", "name": "Borosil Chef Delite 300W Hand Blender", "url": "https://myborosil.com/products/chef-delite-300-w-hand-blender"},
    {"cat": "Kitchen Appliances", "name": "Wonderchef Nutri-Blend 400W Mixer", "url": "https://www.wonderchef.com/products/nutri-blend-400w-mixer-grinder-blender-3-unbreakable-jars"}
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

print("Executing test_discover_all_8...")
verified_list = []
rejected_list = []

for item in candidates_8:
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
            
            imgs = [img.get("src") for img in soup.find_all("img") if img.get("src") and not any(x in img.get("src") for x in ["icon", "logo", "svg", "pixel"])]
            
            page_lower = (html[:5000] + title + h1).lower()
            is_not_found = status == 404 or "404" in title or "page not found" in page_lower or "oops" in title.lower() or "not found" in h1.lower()
            is_blocked = status in [403, 503] or "access denied" in page_lower or "captcha" in page_lower
            
            if status == 200 and not is_not_found and not is_blocked and (h1 or len(title) > 5) and len(imgs) > 0:
                print(f"[VERIFIED] {cat} | {name}")
                print(f"   HTTP: {status} | Canonical URL: {final_url}")
                print(f"   Title: {title[:70]}")
                print(f"   H1: {h1[:70]}")
                print(f"   Images: {len(imgs)}\n")
                verified_list.append({
                    "category": cat,
                    "name": name,
                    "canonical_url": final_url,
                    "http": status,
                    "title": title or h1,
                    "images_count": len(imgs)
                })
            else:
                reason = "404 Not Found" if is_not_found else ("Access Blocked" if is_blocked else f"HTTP {status}")
                print(f"[REJECTED] {cat} | {name} -> {reason}\n")
                rejected_list.append({"url": url, "reason": reason})
    except Exception as e:
        print(f"[REJECTED] {cat} | {name} -> Error: {e}\n")
        rejected_list.append({"url": url, "reason": str(e)})

print(f"\nFinal Summary: {len(verified_list)} Verified URLs across categories!")
