# coded by github.com/leoniofficials
import requests
import time
import re
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import unquote

# coded by github.com/leoniofficials
WEBHOOK_URL = "DISCORD_HOOK_BURAYA_GIRILECEK"
DISCORD_USER_ID = "DISCORD_USERID_BURAYA_GIRILECEK"

# coded by github.com/leoniofficials
def get_price_selenium(market_url):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-background-networking")
        chrome_options.add_argument("--disable-sync")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.get(market_url)
        time.sleep(4)

        try:
            price_elem = driver.find_element(By.ID, "market_commodity_forsale")
            match = re.search(r"\$\d+(\.\d+)?", price_elem.text)
            if match:
                price = float(match.group().replace("$", ""))
                driver.quit()
                return price
        except:
            pass

        driver.quit()
    except Exception as e:
        print(f"Selenium hatası: {e}")
    return None

# coded by github.com/leoniofficials
def get_icon_url(item_name):
    headers = {"User-Agent": "Mozilla/5.0"}
    params = {
        "query": item_name,
        "appid": 730,
        "count": 1,
        "norender": 1
    }
    try:
        r = requests.get(
            "https://steamcommunity.com/market/search/render/",
            params=params,
            headers=headers,
            timeout=10
        )
        r.raise_for_status()
        data = r.json()
        result = data.get("results", [])[0]
        icon = result.get("asset_description", {}).get("icon_url")
        if icon:
            return f"https://community.cloudflare.steamstatic.com/economy/image/{icon}"
    except Exception as e:
        print(f"Icon alınamadı: {e}")
    return None

# coded by github.com/leoniofficials
def send_discord_status(item_name, url, icon_url, current_price, target_price):
    data = {
        "content": f"<@{DISCORD_USER_ID}>",
        "embeds": [
            {
                "title": f"Takip Başladı: {unquote(item_name)}",
                "url": url,
                "description": f"Anlık Fiyat: ${current_price:.2f}\nHedef Fiyat: ${target_price:.2f}",
                "color": 0x3498db,
                "thumbnail": {"url": icon_url} if icon_url else {}
            }
        ]
    }
    requests.post(WEBHOOK_URL, json=data)

# coded by github.com/leoniofficials
def send_discord_alert(item_name, url, current_price):
    data = {
        "content": f"<@{DISCORD_USER_ID}>",
        "embeds": [
            {
                "title": f"Fiyat Uyarısı: {unquote(item_name)}",
                "url": url,
                "description": f"Anlık Fiyat: ${current_price:.2f}\nBelirlediğin hedef fiyata ulaştı!",
                "color": 0xFF0000
            }
        ]
    }
    requests.post(WEBHOOK_URL, json=data)

# coded by github.com/leoniofficials
def takip_et(market_url, target_price):
    try:
        parts = market_url.split("/market/listings/")[1].split("/")
        item_name = parts[1]
    except:
        print("URL ayrıştırılamadı.")
        return

    print(f"Takip başlatıldı: {market_url} - Hedef fiyat: ${target_price}")
    icon_url = get_icon_url(item_name)

    first_price = get_price_selenium(market_url)
    if first_price:
        send_discord_status(item_name, market_url, icon_url, first_price, target_price)
    else:
        print("İlk fiyat alınamadı.")

    while True:
        current_price = get_price_selenium(market_url)
        if current_price:
            print(f"{unquote(item_name)} fiyatı: ${current_price}")
            if current_price <= target_price:
                send_discord_alert(item_name, market_url, current_price)
                time.sleep(120)
        else:
            print("Fiyat alınamadı, tekrar deneniyor...")
        time.sleep(20)

# coded by github.com/leoniofficials
while True:
    market_url = input("\n Steam Market URL: ").strip()
    target_price = float(input("Fiyat bu seviyeye düşünce bildirim gelsin (USD$): ").strip())

    thread = threading.Thread(target=takip_et, args=(market_url, target_price), daemon=True)
    thread.start()

    devam = input("Yeni bir takip başlatmak için 't' yaz, çıkmak için ENTER: ").strip().lower()
    if devam != 't':
        print("Çıkılıyor...")
        break

# coded by github.com/leoniofficials

# soruların mı var?
# discord: leoniofficials
