import os
import time
import random
import pandas as pd
import cloudscraper
from bs4 import BeautifulSoup

START_SEASON = 1950
END_SEASON = 2025

BASE_URL = "https://www.basketball-reference.com/leagues/NBA_{}_advanced.html"
PLAYOFFS_URL = "https://www.basketball-reference.com/playoffs/NBA_{}_advanced.html"
#playoffs não funcionou, preferi fazer um código separado

OUTPUT_DIR = "PlayerSeasonStats"
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
                print(f"429 recebido. Esperando {wait}s antes de tentar novamente...")
                time.sleep(wait)
                continue

            response.raise_for_status()
            return response

        except Exception as e:
            print(f"Tentativa {attempt+1}/{max_retries} falhou: {e}")
            time.sleep(random.uniform(10, 20))

    print(f"Falha definitiva ao acessar: {url}")
    return None

for season in range(START_SEASON, END_SEASON + 1):

    dfs = []

    url = BASE_URL.format(season)
    print(f"\nRegular Season: {url}")

    response = safe_get(scraper, url)
    if response is not None:
        html = response.text.replace("<!--", "").replace("-->", "")
        soup = BeautifulSoup(html, "lxml")

        table_reg = soup.find("table", id="advanced")
        if table_reg is not None:
            df_reg = pd.read_html(str(table_reg))[0]
            df_reg = df_reg[df_reg["Rk"] != "Rk"]
            df_reg["season"] = season
            df_reg["is_playoff"] = False
            dfs.append(df_reg)
        else:
            print(f"Regular season não encontrada para {season}")

    time.sleep(random.uniform(3, 6))

    url_po = PLAYOFFS_URL.format(season)
    print(f"Playoffs: {url_po}")

    response_po = safe_get(scraper, url_po)
    if response_po is not None:
        html_po = response_po.text.replace("<!--", "").replace("-->", "")
        soup_po = BeautifulSoup(html_po, "lxml")

        table_po = soup_po.find("table", id="advanced")
        if table_po is not None:
            df_po = pd.read_html(str(table_po))[0]
            df_po = df_po[df_po["Rk"] != "Rk"]
            df_po["season"] = season
            df_po["is_playoff"] = True
            dfs.append(df_po)
        else:
            print(f"Playoffs não encontrados para {season}")
    else:
        print(f"Sem playoffs para {season}")

    if not dfs:
        print(f"Nenhum dado encontrado para {season}")
        continue

    df = pd.concat(dfs, ignore_index=True)
    df = df.apply(pd.to_numeric, errors='ignore')

    filename = f"player_season_stats_{season}.csv"
    filepath = os.path.join(OUTPUT_DIR, filename)
    df.to_csv(filepath, index=False, encoding="utf-8")

    print(f"Salvo: {filepath}")

    sleep_time = random.uniform(6, 12)
    print(f"Dormindo {sleep_time:.1f}s...")
    time.sleep(sleep_time)