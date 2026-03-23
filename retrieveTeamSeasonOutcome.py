import os
import time
import random
import pandas as pd
import cloudscraper
from bs4 import BeautifulSoup

START_SEASON = 1950
END_SEASON = 2025

BASE_URL = "https://www.basketball-reference.com/playoffs/NBA_{}.html"
OUTPUT_FILE = "team_season_outcomes.csv"

scraper = cloudscraper.create_scraper()

all_rows = []

def extract_playoff_results(soup):

    results = {
        "playoff_teams": set(),
        "conf_finalists": set(),
        "champion": None
    }

    table = soup.find("table", id="all_playoffs")

    if table is None:
        return results

    df = pd.read_html(str(table))[0]

    for _, row in df.iterrows():

        round_name = str(row[0])
        matchup = str(row[1])

        if "over" not in matchup:
            continue

        winner = matchup.split(" over ")[0].strip()
        loser = matchup.split(" over ")[1].split("(")[0].strip()

        results["playoff_teams"].add(winner)
        results["playoff_teams"].add(loser)

        # campeão
        if "Finals" in round_name and "Conference" not in round_name:
            results["champion"] = winner

        if "Conference Finals" in round_name:
            results["conf_finalists"].add(winner)
            results["conf_finalists"].add(loser)

    return results

def get_team_name_mapping(soup):
    mapping = {}

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if "/teams/" in href:
            parts = href.split("/")
            if len(parts) > 2:
                code = parts[2]
                name = a.text.strip()
                mapping[name] = code

    return mapping

for season in range(START_SEASON, END_SEASON + 1):
    url = BASE_URL.format(season)
    print(f"📥 Baixando: {url}")

    try:
        response = scraper.get(url)

        if response.status_code == 429:
            wait = random.uniform(20, 40)
            print(f"⏳ 429 recebido, esperando {wait:.1f}s...")
            time.sleep(wait)
            continue

        if response.status_code == 404:
            print(f"🚫 Página não existe para {season}")
            continue

        response.raise_for_status()

    except Exception as e:
        print(f"⚠️ Erro na temporada {season}: {e}")
        continue

    html = response.text.replace("<!--", "").replace("-->", "")
    soup = BeautifulSoup(html, "lxml")

    results = extract_playoff_results(soup)

    playoff_teams = results["playoff_teams"]
    conf_finalists = results["conf_finalists"]
    champion = results["champion"]

    mapping = get_team_name_mapping(soup)

    playoff_teams = {mapping.get(t, t) for t in playoff_teams}
    conf_finalists = {mapping.get(t, t) for t in conf_finalists}
    champion = mapping.get(champion, champion)

    for team in playoff_teams:
        all_rows.append({
            "team": team,
            "season": season,
            "reached_playoffs": 1,
            "reached_conf_finals": int(team in conf_finalists),
            "champion": int(team == champion)
        })

    time.sleep(random.uniform(5, 10))


df = pd.DataFrame(all_rows)

all_teams = df["team"].unique()

full_rows = []
for season in df["season"].unique():
    season_df = df[df["season"] == season]
    teams_in_season = set(season_df["team"])

    for team in all_teams:
        if team not in teams_in_season:
            full_rows.append({
                "team": team,
                "season": season,
                "reached_playoffs": 0,
                "reached_conf_finals": 0,
                "champion": 0
            })

df = pd.concat([df, pd.DataFrame(full_rows)], ignore_index=True)

df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

print(f"\nArquivo salvo: {OUTPUT_FILE}")