import json
import time
from datetime import datetime, timezone
from pathlib import Path
from playwright.sync_api import sync_playwright

CHANNELS_FILE = "channels.json"
JSON_FILE = "playlist.json"
M3U_FILE = "playlist.m3u"

# Load channels from JSON
def load_channels():
    with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# Fetch .m3u8 URL
def fetch_m3u8(channel_code, timeout=20):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"])
        page = browser.new_page()
        m3u8_url = None

        def log_request(request):
            nonlocal m3u8_url
            url = request.url
            if url.endswith(".m3u8") and "md5=" in url and "expires=" in url:
                m3u8_url = url

        page.on("request", log_request)

        page.goto(f"https://streamcrichd.com/update/{channel_code}.php", timeout=60000)
        try:
            # Try to play video if available
            page.wait_for_selector("video", timeout=5000)
            page.evaluate("() => { const v=document.querySelector('video'); if(v)v.play(); }")
        except:
            pass

        # Wait for .m3u8 request
        for _ in range(timeout):
            if m3u8_url:
                break
            time.sleep(1)

        browser.close()
        return m3u8_url

# Save JSON
def save_json(channels_data):
    data = {
        "last_update": datetime.now(timezone.utc).isoformat(),
        "channels": channels_data
    }
    Path(JSON_FILE).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

# Save M3U
def save_m3u(channels_data):
    lines = ["#EXTM3U"]
    for ch in channels_data:
        if ch.get("url"):
            lines.append(f'#EXTINF:-1 tvg-id="{ch["tvg-id"]}" tvg-logo="{ch["tvg-logo"]}", {ch["name"]}')
            lines.append(ch["url"])
    Path(M3U_FILE).write_text("\n".join(lines)+"\n", encoding="utf-8")

def main():
    channels = load_channels()
    result = []

    for ch in channels:
        try:
            print(f"Fetching {ch['name']}...")
            url = fetch_m3u8(ch["code"])
            if not url:
                print(f"❌ M3U8 not found for {ch['name']}")
                continue
            print("✅ Found:", url)
            result.append({
                "tvg-id": ch["tvg-id"],
                "tvg-logo": ch.get("tvg-logo",""),
                "name": ch["name"],
                "url": url
            })
        except Exception as e:
            print(f"❌ Error fetching {ch['name']}: {e}")

    save_json(result)
    save_m3u(result)
    print("🎉 Playlist updated!")

if __name__ == "__main__":
    main()
