import asyncio
import json
from pyppeteer import launch
from datetime import datetime

CHANNEL_INFO = {
    "tvg-id": "ptvpk",
    "tvg-logo": "https://upload.wikimedia.org/wikipedia/en/7/72/PTV_Sports.png",
    "name": "PTV Sports"
}

SOURCE_URL = "https://streamcrichd.com/update/ptv.php"
JSON_FILE = "playlist.json"
M3U_FILE = "playlist.m3u"

async def fetch_m3u8():
    browser = await launch(headless=True, args=["--no-sandbox"])
    page = await browser.newPage()
    m3u8_url = None

    async def handle_response(resp):
        nonlocal m3u8_url
        url = resp.url
        if ".m3u8" in url and "expires=" in url and "md5=" in url:
            m3u8_url = url

    page.on("response", handle_response)

    await page.goto(SOURCE_URL, timeout=60000)
    await page.waitForTimeout(8000)
    await browser.close()

    if not m3u8_url:
        raise Exception("M3U8 লিঙ্ক পাওয়া যায়নি")
    return m3u8_url

def save_json(m3u8_url):
    data = {
        "last_update": datetime.utcnow().isoformat(),
        "channel": {
            "tvg-id": CHANNEL_INFO["tvg-id"],
            "tvg-logo": CHANNEL_INFO["tvg-logo"],
            "name": CHANNEL_INFO["name"],
            "url": m3u8_url
        }
    }
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def save_m3u(m3u8_url):
    content = (
        "#EXTM3U\n"
        f'#EXTINF:-1 tvg-id="{CHANNEL_INFO["tvg-id"]}" '
        f'tvg-logo="{CHANNEL_INFO["tvg-logo"]}", {CHANNEL_INFO["name"]}\n'
        f"{m3u8_url}\n"
    )
    with open(M3U_FILE, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    m3u8_url = asyncio.get_event_loop().run_until_complete(fetch_m3u8())
    print("✅ M3U8 Found:", m3u8_url)
    save_json(m3u8_url)
    save_m3u(m3u8_url)

if __name__ == "__main__":
    main()
