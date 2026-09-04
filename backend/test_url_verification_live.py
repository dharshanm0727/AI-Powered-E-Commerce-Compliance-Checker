import httpx
import bs4
import json
import urllib.parse
import re

test_urls = [
    # Dead URL to test
    {"label": "Dead Amazon Rice URL", "url": "https://www.amazon.in/Fortune-Everyday-Basmati-Rice-5kg/dp/B07R9D971S"},
    # Candidate URLs across different platforms
    {"label": "BigBasket Fortune Rice", "url": "https://www.bigbasket.com/pd/40072483/fortune-everyday-basmati-rice-5-kg-pouch/"},
    {"label": "Blinkit Fortune Rice", "url": "https://blinkit.com/prn/fortune-everyday-basmati-rice/prid/43126"},
    {"label": "Amazon Optimum Nutrition", "url": "https://www.amazon.in/Optimum-Nutrition-Standard-Naturally-Flavored/dp/B000GIQT06"},
    {"label": "Official ON India", "url": "https://www.optimumnutrition.co.in/gold-standard-100-whey"},
    {"label": "BigBasket Real Orange Juice", "url": "https://www.bigbasket.com/pd/266547/real-fruit-power-juice-orange-1-l/"},
    {"label": "Tata 1mg Nivea Cream", "url": "https://www.1mg.com/otc/nivea-soft-light-moisturizer-creme-with-vitamin-e-jojoba-oil-for-face-body-hands-otc348911"},
    {"label": "Croma Philips LED", "url": "https://www.croma.com/philips-stellar-bright-9w-b22-led-bulb-cool-day-white-/p/231189"},
    {"label": "Amazon Prestige Kettle", "url": "https://www.amazon.in/Prestige-Electric-Kettle-PKOSS-1500/dp/B0756K54P5"},
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1"
}

print("Running live URL HTTP testing...")
for item in test_urls:
    url = item["url"]
    label = item["label"]
    try:
        with httpx.Client(headers=headers, follow_redirects=True, timeout=15.0) as client:
            resp = client.get(url)
            status = resp.status_code
            final_url = str(resp.url)
            html = resp.text
            soup = bs4.BeautifulSoup(html, "html.parser")
            
            title = soup.title.string.strip() if soup.title and soup.title.string else ""
            h1 = soup.find("h1").get_text(strip=True) if soup.find("h1") else ""
            
            is_page_not_found = False
            page_lower = (html[:5000] + title).lower()
            if "page not found" in page_lower or "404" in title or "looking for something?" in page_lower or "we're sorry" in page_lower or "dogs of amazon" in page_lower:
                is_page_not_found = True
            
            is_blocked = False
            if status in [403, 503] or "captcha" in page_lower or "robot" in page_lower or "blocked" in page_lower or "access denied" in page_lower:
                is_blocked = True
                
            print(f"[{label}] -> Status: {status} | Final URL: {final_url[:60]}... | Title: {title[:50]} | 404/NotFound: {is_page_not_found} | Blocked: {is_blocked}")
    except Exception as e:
        print(f"[{label}] -> ERROR: {e}")
