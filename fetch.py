import requests
import re
import json
from datetime import datetime

# চ্যানেল ইনফো
CHANNEL_INFO = {
    "tvg-id": "ptvpk",
    "tvg-logo": "https://upload.wikimedia.org/wikipedia/en/7/72/PTV_Sports.png",
    "name": "PTV Sports"
}

# সোর্স লিঙ্ক
SOURCE_URL = "https://streamcrichd.com/update/ptv.php"

# আউটপুট ফাইল
JSON_FILE = "playlist.json"
M3U_FILE = "playlist.m3u"

def fetch_m3u8():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/124.0.0.0 Safari/537.36"
    }
    r = requests.get(SOURCE_URL, headers=headers, timeout=15)
    r.raise_for_status()

    # Regex দিয়ে m3u8 বের করা
    match = re.search(r"(https://[^\s'\"]+\.m3u8\?[^'\"]+)", r.text)
    if match:
        return match.group(1)
    else:
        raise Exception("M3U8 URL পাওয়া যায়নি")

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
    try:
        m3u8_url = fetch_m3u8()
        print("✅ M3U8 Found:", m3u8_url)
        save_json(m3u8_url)
        save_m3u(m3u8_url)
    except Exception as e:
        print("❌ Error:", str(e))

if __name__ == "__main__":
    main()
