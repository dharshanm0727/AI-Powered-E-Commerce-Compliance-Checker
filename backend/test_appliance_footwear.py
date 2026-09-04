import httpx
import bs4
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

appliance_footwear_candidates = [
    # Footwear
    {"cat": "Footwear", "name": "Liberty Shoes Leap7X Sports Shoes", "url": "https://www.libertyshoesonline.com/leap7x-by-liberty-men-black-lacing-sports-shoes-el-209.html"},
    {"cat": "Footwear", "name": "Woodland Men Camel Casual Shoes", "url": "https://www.woodlandworldwide.com/product-detail/O_GC_1435114_CAMEL"},
    {"cat": "Footwear", "name": "Woodland Khaki Casual Sneakers", "url": "https://www.woodlandworldwide.com/productinfo/FGC026042451A-KHAKI"},
    
    # Kitchen Appliance
    {"cat": "Kitchen Appliances", "name": "Prestige Iris Plus Mixer Grinder", "url": "https://prestigexclusive.in/products/prestige-iris-plus-750-watt-mixer-grinder-with-4-jars-black"},
    {"cat": "Kitchen Appliances", "name": "Prestige PKOSS Electric Kettle 1.5L", "url": "https://prestigexclusive.in/products/prestige-pkoss-1-5-litre-1500w-electric-kettle-stainless-steel"},
    {"cat": "Kitchen Appliances", "name": "Butterfly Jet Elite 750W Mixer Grinder", "url": "https://www.butterflyindia.com/product/jet-elite-750-watt-mixer-grinder-with-3-jars-grey/"},
    {"cat": "Kitchen Appliances", "name": "Kent Ultra Storage Water Purifier", "url": "https://www.kent.co.in/water-purifiers/uv/kent-ultra-storage"}
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

print("Testing Appliance and Footwear URLs live...")
for item in appliance_footwear_candidates:
    url = item["url"]
    try:
        with httpx.Client(headers=headers, follow_redirects=True, timeout=12.0) as client:
            resp = client.get(url)
            status = resp.status_code
            soup = bs4.BeautifulSoup(resp.text, "html.parser")
            title = soup.title.string.strip() if soup.title and soup.title.string else ""
            h1 = soup.find("h1").get_text(strip=True) if soup.find("h1") else ""
            imgs = [img.get("src") for img in soup.find_all("img") if img.get("src")]
            
            page_lower = (resp.text[:4000] + title + h1).lower()
            is_404 = status == 404 or "404" in title or "page not found" in page_lower or "not found" in h1.lower()
            
            print(f"[{item['cat']} - {item['name']}]")
            print(f"   HTTP: {status} | Final URL: {resp.url}")
            print(f"   Title: {title[:60]}")
            print(f"   H1: {h1[:60]}")
            print(f"   Images: {len(imgs)} | 404: {is_404}\n")
    except Exception as e:
        print(f"[{item['cat']} - {item['name']}] -> Error: {e}\n")
