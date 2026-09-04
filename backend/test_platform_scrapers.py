import httpx
import bs4
import json
import re

test_targets = [
    # Boat Lifestyle (Electronics/Headphones)
    {"cat": "Electronics", "name": "boAt Airdopes 141", "url": "https://www.boat-lifestyle.com/products/airdopes-141"},
    # Mamaearth (Cosmetics)
    {"cat": "Cosmetics", "name": "Mamaearth Onion Shampoo", "url": "https://mamaearth.in/product/onion-shampoo-for-hair-fall-control"},
    # Nykaa (Cosmetics)
    {"cat": "Cosmetics", "name": "Maybelline Mascara", "url": "https://www.nykaa.com/maybelline-new-york-lash-sensational-waterproof-mascara/p/35451"},
    # Bewakoof (Clothing)
    {"cat": "Clothing", "name": "Mens Black T-Shirt", "url": "https://www.bewakoof.com/p/men-black-solid-round-neck-t-shirt"},
    # Kapiva (Health/Food)
    {"cat": "Health Supplements", "name": "Kapiva Amla Juice", "url": "https://kapiva.in/ayurvedic-juices/wild-amla-juice-1l/"},
    # Organic India (Food)
    {"cat": "Food", "name": "Organic India Tulsi Green Tea", "url": "https://organicindia.com/products/tulsi-green-tea-classic-25-tea-bags"},
    # Daawat / LT Foods (Food)
    {"cat": "Food", "name": "Daawat Rozana Basmati Rice", "url": "https://www.flipkart.com/daawat-rozana-super-basmati-rice-medium-grain/p/itmfc44d852cb7ba"},
    # Decathlon (Sports/Footwear)
    {"cat": "Footwear", "name": "Kalenji Running Shoes", "url": "https://www.decathlon.in/p/8559090/running-shoes/men-running-shoes-run-cushion-black"},
    # Croma (Appliances)
    {"cat": "Appliances", "name": "Philips Trimmer", "url": "https://www.reliancedigital.in/philips-bt1232-15-skin-friendly-beard-trimmer-blue/p/491901174"},
    # Tata 1mg (Medicines / Health)
    {"cat": "Health", "name": "Dettol Antiseptic", "url": "https://www.apollopharmacy.in/otc/dettol-antiseptic-liquid-550ml"},
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

print("Testing direct brand stores and e-commerce platforms...")
for t in test_targets:
    url = t["url"]
    try:
        with httpx.Client(headers=headers, follow_redirects=True, timeout=12.0) as client:
            resp = client.get(url)
            status = resp.status_code
            soup = bs4.BeautifulSoup(resp.text, "html.parser")
            title = soup.title.string.strip() if soup.title and soup.title.string else ""
            h1 = soup.find("h1").get_text(strip=True) if soup.find("h1") else ""
            
            # Check price/mrp
            text_snippet = soup.get_text(separator=" ", strip=True)[:400]
            
            # Check images
            imgs = [img.get("src") for img in soup.find_all("img") if img.get("src")]
            
            print(f"[{t['cat']} - {t['name']}]")
            print(f"  HTTP: {status} | URL: {resp.url}")
            print(f"  Title: {title[:70]}")
            print(f"  H1: {h1[:70]}")
            print(f"  Images found: {len(imgs)}")
            print(f"  Text preview: {text_snippet[:150]}...\n")
    except Exception as e:
        print(f"[{t['cat']} - {t['name']}] -> Error: {e}\n")
