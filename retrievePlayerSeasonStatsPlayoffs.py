import os
import time
import random
import pandas as pd
import cloudscraper
from bs4 import BeautifulSoup

START_SEASON = 1950
END_SEASON = 2025

PLAYOFFS_URL = "https://www.basketball-reference.com/playoffs/NBA_{}_advanced.html"

OUTPUT_DIR = "PlayerSeasonStatsPlayoffs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


scraper = cloudscraper.create_scraper(browser={
    "browser": "chrome",
    "platform": "windows",
    "mobile": False
})


def safe_get(scraper, url, max_retries=5):
    for attempt in range(max_retries):
        try:
            response = scraper.get(url)

            if response.status_code == 429:
                wait = 20 * (attempt + 1)
                print(f"429 recebido. Esperando {wait}s...")
                time.sleep(wait)
                continue

            response.raise_for_status()
            return response

        except Exception as e:
            print(f"Tentativa {attempt+1}/{max_retries} falhou: {e}")
            time.sleep(random.uniform(10, 20))

    print(f"Falha definitiva: {url}")
    return None

for season in range(START_SEASON, END_SEASON + 1):

    url = PLAYOFFS_URL.format(season)
    print(f"\n📥 Playoffs: {url}")

    response = safe_get(scraper, url)
    if response is None:
        continue

    html = response.text.replace("<!--", "").replace("-->", "")
    soup = BeautifulSoup(html, "lxml")

    table = soup.find("table", id="advanced_stats")

    if table is None:
        print(f"⚠️ Sem tabela de playoffs para {season}")
        continue

    df = pd.read_html(str(table))[0]
    df = df[df["Rk"] != "Rk"]
    df["season"] = season
    df["is_playoff"] = True

    df = df.apply(pd.to_numeric, errors='ignore')


    filename = f"player_playoff_stats_{season}.csv"
    filepath = os.path.join(OUTPUT_DIR, filename)
    df.to_csv(filepath, index=False, encoding="utf-8")

    print(f"Salvo: {filepath}")

    sleep_time = random.uniform(6, 12)
    print(f"Dormindo {sleep_time:.1f}s...")
    time.sleep(sleep_time)