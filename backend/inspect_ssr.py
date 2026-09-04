import httpx
import bs4
import json
import re

url = "https://www.jiomart.com/p/groceries/tata-iodised-salt-1-kg/490000073"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

with httpx.Client(headers=headers, follow_redirects=True, timeout=12.0) as client:
    r = client.get(url)
    soup = bs4.BeautifulSoup(r.text, "html.parser")
    
    # Check JSON-LD
    scripts = soup.find_all("script", type="application/ld+json")
    print(f"Found {len(scripts)} ld+json scripts")
    for s in scripts:
        try:
            data = json.loads(s.string)
            print("LD+JSON:", json.dumps(data, indent=2)[:300])
        except Exception as e:
            print("Error parsing json:", e)
            
    # Check Next.js __NEXT_DATA__
    next_data = soup.find("script", id="__NEXT_DATA__")
    if next_data:
        print("Found __NEXT_DATA__!")
        nd = json.loads(next_data.string)
        props = nd.get("props", {}).get("pageProps", {})
        print("Next.js pageProps keys:", list(props.keys())[:10])
        prod = props.get("productData", {}) or props.get("initialData", {}) or props.get("data", {})
        print("Product data preview:", str(prod)[:300])
