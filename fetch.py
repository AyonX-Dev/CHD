import json
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

CHANNELS_FILE = "channels.json"

def load_channels():
    with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def fetch_m3u8(channel_code):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        m3u8_url = None

        def log_response(response):
            nonlocal m3u8_url
            url = response.url
            if ".m3u8" in url and "md5=" in url and "expires=" in url:
                m3u8_url = url

        page.on("response", log_response)
        page.goto(f"https://streamcrichd.com/update/{channel_code}.php", timeout=60000)

        try:
            page.wait_for_selector("video", timeout=5000)
            page.evaluate("() => { const v=document.querySelector('video'); if(v)v.play(); }")
        except:
            pass

        page.wait_for_timeout(8000)
        browser.close()
        return m3u8_url

def main():
    channels = load_channels()
    result = []

    for ch in channels:
        try:
            url = fetch_m3u8(ch["code"])
            ch_data = {
                "tvg-id": ch["tvg-id"],
                "tvg-logo": ch["tvg-logo"],
                "name": ch["name"],
                "url": url
            }
            result.append(ch_data)
        except Exception as e:
            print(f"❌ Error fetching {ch['name']}: {e}")

    data_str = json.dumps({
        "last_update": datetime.now(timezone.utc).isoformat(),
        "channels": result
    }, indent=2)

    m3u_str = "#EXTM3U\n"
    for ch in result:
        if ch.get("url"):
            m3u_str += f'#EXTINF:-1 tvg-id="{ch["tvg-id"]}" tvg-logo="{ch["tvg-logo"]}", {ch["name"]}\n'
            m3u_str += f'{ch["url"]}\n'

    return data_str, m3u_str

if __name__ == "__main__":
    data, m3u = main()
    print("JSON_START")
    print(data)
    print("JSON_END")
    print("M3U_START")
    print(m3u)
    print("M3U_END")
