import httpx
import bs4
import sys

sys.stdout.reconfigure(encoding='utf-8')

asian_urls = [
    "https://asianfootwears.com/products/asian-tarzan-11-white-running-shoes-for-men",
    "https://asianfootwears.com/products/unicorn-13-mens-sneakers",
    "https://asianfootwears.com/products/delta-25-sports-running-shoes-for-men",
    "https://asianfootwears.com/products/superwalk-08-running-shoes"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

for u in asian_urls:
    try:
        with httpx.Client(headers=headers, follow_redirects=True, timeout=12.0) as client:
            r = client.get(u)
            soup = bs4.BeautifulSoup(r.text, "html.parser")
            h1 = soup.find("h1").get_text(strip=True) if soup.find("h1") else ""
            title = soup.title.string.strip() if soup.title and soup.title.string else ""
            print(f"URL: {r.url} | Status: {r.status_code}")
            print(f"H1: {h1} | Title: {title}\n")
    except Exception as e:
        print(f"Error {u}: {e}\n")
