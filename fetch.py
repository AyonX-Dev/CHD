import json
from datetime import datetime
from playwright.sync_api import sync_playwright

# চ্যানেল লিস্ট
CHANNELS = [
    {"code": "ptv", "tvg-id": "ptvpk", "tvg-logo": "https://upload.wikimedia.org/wikipedia/en/7/72/PTV_Sports.png", "name": "PTV Sports"},
    {"code": "sonyten1", "tvg-id": "sonyten1", "tvg-logo": "", "name": "Sony Ten 1"},
    {"code": "willowcricket", "tvg-id": "willowcricket", "tvg-logo": "", "name": "Willow Cricket"},
    {"code": "tensp", "tvg-id": "tensp", "tvg-logo": "", "name": "Ten Sports Plus"},
    {"code": "asportshd", "tvg-id": "asportshd", "tvg-logo": "", "name": "A Sports HD"},
    {"code": "sonymax", "tvg-id": "sonymax", "tvg-logo": "", "name": "Sony Max"},
    {"code": "sscricket", "tvg-id": "sscricket", "tvg-logo": "", "name": "Sony Six Cricket"},
    {"code": "skys2", "tvg-id": "skys2", "tvg-logo": "", "name": "Sky Sports 2"}
]

def fetch_m3u8(channel_code):
    """
    Page open + video play + network capture
    """
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

        # video play চেষ্টা
        try:
            page.wait_for_selector("video", timeout=5000)  # 5 সেকেন্ড
            page.evaluate("() => { const v=document.querySelector('video'); if(v)v.play(); }")
        except:
            pass

        # network capture জন্য wait
        page.wait_for_timeout(8000)  # 8 সেকেন্ড
        browser.close()
        return m3u8_url

def main():
    result = []
    for ch in CHANNELS:
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

    # JSON তৈরি
    data_str = json.dumps({"last_update": datetime.utcnow().isoformat(), "channels": result}, indent=2)
    
    # M3U তৈরি
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
