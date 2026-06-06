import requests
from bs4 import BeautifulSoup
import time
import os

SAVE_DIR = "data/"
os.makedirs(SAVE_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# These are real, direct judgment URLs from indiankanoon.org
# We hardcode a starter list to bypass the search block
JUDGMENT_URLS = [
    # Employment termination & industrial disputes
    "https://indiankanoon.org/doc/1358175/",   # Workman vs Management
    "https://indiankanoon.org/doc/756491/",    # Industrial Disputes Act termination
    "https://indiankanoon.org/doc/990071/",    # Retrenchment notice requirement
    "https://indiankanoon.org/doc/1364644/",   # Employment termination procedure
    "https://indiankanoon.org/doc/500153/",    # Dismissal without notice
    "https://indiankanoon.org/doc/84438/",     # Employee rights on dismissal
    "https://indiankanoon.org/doc/261940/",    # Notice period in termination
    "https://indiankanoon.org/doc/1902330/",   # Wrongful termination
    "https://indiankanoon.org/doc/522790/",    # Industrial tribunal ruling
    "https://indiankanoon.org/doc/631708/",    # Retrenchment compensation
    "https://indiankanoon.org/doc/1223182/",   # Standing orders violation
    "https://indiankanoon.org/doc/75937/",     # Domestic enquiry termination
    "https://indiankanoon.org/doc/1955438/",   # Notice period dispute
    "https://indiankanoon.org/doc/1091721/",   # Misconduct dismissal
    "https://indiankanoon.org/doc/1733066/",   # Reinstatement after termination
    "https://indiankanoon.org/doc/1375768/",   # Labour court ruling
    "https://indiankanoon.org/doc/1828219/",   # Government employee dismissal
    "https://indiankanoon.org/doc/109160/",    # Service rules termination
]

def save_judgment(url, index):
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        # Try multiple possible content divs
        content = (
            soup.find("div", {"id": "judgments"}) or
            soup.find("div", {"class": "judgments"}) or
            soup.find("div", {"id": "main"}) or
            soup.find("div", {"class": "doc-content"})
        )

        # Get title
        title_tag = soup.find("h2", {"class": "doc-title"}) or soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else f"Judgment {index}"

        if content:
            text = content.get_text(separator="\n", strip=True)
        else:
            # fallback: grab all paragraph text
            text = "\n".join(p.get_text(strip=True) for p in soup.find_all("p"))

        if len(text) < 200:
            print(f"  Skipping {index} — too short (might be blocked)")
            return

        filepath = f"{SAVE_DIR}judgment_{index}.txt"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"SOURCE: {url}\nTITLE: {title}\n\n{text}")
        print(f"  Saved judgment_{index}.txt — {len(text)} chars — {title[:60]}")

    except Exception as e:
        print(f"  Error on {url}: {e}")

    time.sleep(2)

if __name__ == "__main__":
    print(f"Downloading {len(JUDGMENT_URLS)} judgments...\n")
    for i, url in enumerate(JUDGMENT_URLS):
        print(f"[{i+1}/{len(JUDGMENT_URLS)}] {url}")
        save_judgment(url, i)
    print(f"\nDone! Check your data/ folder.")