import json, os, random, re
import requests
from bs4 import BeautifulSoup

BASE = "https://paulgraham.com/"
SENT_FILE = "sent.json"
SKIP = {"articles.html", "index.html", "rss.html", "bio.html", "books.html",
        "faq.html", "raq.html", "quo.html", "arc.html"}

def get_essays():
    html = requests.get(BASE + "articles.html", timeout=30).text
    soup = BeautifulSoup(html, "html.parser")
    essays = {}
    for a in soup.find_all("a", href=True):
        href, title = a["href"], a.get_text(strip=True)
        if re.fullmatch(r"[a-z0-9]+\.html", href) and href not in SKIP and title:
            essays[href] = title
    return essays

def load_sent():
    if os.path.exists(SENT_FILE):
        with open(SENT_FILE) as f:
            return json.load(f)
    return []

def main():
    essays = get_essays()
    sent = [s for s in load_sent() if s in essays]

    remaining = [h for h in essays if h not in sent]
    if not remaining:          # full list done -> start a new cycle
        sent, remaining = [], list(essays)

    pick = random.choice(remaining)
    sent.append(pick)

    text = f"📖 Essay of the day\n\n{essays[pick]}\n{BASE}{pick}"
    r = requests.post(
        f"https://api.telegram.org/bot{os.environ['BOT_TOKEN']}/sendMessage",
        data={"chat_id": os.environ["CHAT_ID"], "text": text},
        timeout=30,
    )
    r.raise_for_status()

    with open(SENT_FILE, "w") as f:
        json.dump(sent, f, indent=2)

if __name__ == "__main__":
    main()
