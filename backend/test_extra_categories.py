import httpx
import bs4
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

extra_candidates = [
    # Cosmetic
    {"cat": "Cosmetics", "name": "Minimalist Niacinamide Serum", "url": "https://beminimalist.co/products/niacinamide-5-centella-extract"},
    {"cat": "Cosmetics", "name": "Minimalist Salicylic Acid 2%", "url": "https://beminimalist.co/products/salicylic-acid-2"},
    {"cat": "Cosmetics", "name": "Foxtale Glow Sunscreen SPF 50", "url": "https://foxtale.in/products/glow-sunscreen-spf-50-pa"},
    {"cat": "Cosmetics", "name": "Foxtale Dewy Sunscreen", "url": "https://foxtale.in/products/coverup-dewy-sunscreen-spf-50-pa"},
    
    # Footwear
    {"cat": "Footwear", "name": "RedTape Men Walking Shoes", "url": "https://redtape.com/products/men-black-walking-shoes"},
    {"cat": "Footwear", "name": "Bata Men Formal Shoes", "url": "https://www.bata.com/in/men/shoes/formal-shoes/"},
    
    # Kitchen Appliances
    {"cat": "Kitchen Appliances", "name": "Pigeon Electric Kettle", "url": "https://www.stovekraft.com/products/pigeon-ever-crystal-glass-kettle"},
    {"cat": "Kitchen Appliances", "name": "Borosil Rio Kettle", "url": "https://myborosil.com/products/borosil-rio-electric-kettle-1-5l"},
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

print("Testing extra categories...")
for item in extra_candidates:
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
