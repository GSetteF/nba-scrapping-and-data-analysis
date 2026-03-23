import os
import time
import random
import pandas as pd
import cloudscraper
from bs4 import BeautifulSoup

START_SEASON = 1950
END_SEASON = 1979

BASE_FOLDER = "TeamGames"
os.makedirs(BASE_FOLDER, exist_ok=True)

scraper = cloudscraper.create_scraper()

#dicionário para buscas
TEAM_NAME_TO_ABBR = {
    "Atlanta Hawks": "ATL",
    "Anderson Packers": "AND",
    "Baltimore Bullets": "BAL",
    "Boston Celtics": "BOS",
    "Brooklyn Nets": "BRK",
    "Buffalo Braves": "BUF",
    "Charlotte Hornets": "CHO",
    "Charlotte Bobcats": "CHA",
    "Chicago Bulls": "CHI",
    "Chicago Stags": "CHS",
    "Cincinnati Royals": "CIN",
    "Cleveland Cavaliers": "CLE",
    "Dallas Mavericks": "DAL",
    "Denver Nuggets": "DEN",
    "Detroit Pistons": "DET",
    "Golden State Warriors": "GSW",
    "Houston Rockets": "HOU",
    "Indiana Pacers": "IND",
    "Kansas City Kings": "KCK",
    "Los Angeles Clippers": "LAC",
    "Los Angeles Lakers": "LAL",
    "Memphis Grizzlies": "MEM",
    "Miami Heat": "MIA",
    "Milwaukee Bucks": "MIL",
    "Minnesota Timberwolves": "MIN",
    "New Jersey Nets": "NJN",
    "New Orleans Pelicans": "NOP",
    "New Orleans Hornets": "NOH",
    "New York Knicks": "NYK",
    "Oklahoma City Thunder": "OKC",
    "Orlando Magic": "ORL",
    "Philadelphia 76ers": "PHI",
    "Phoenix Suns": "PHO",
    "Portland Trail Blazers": "POR",
    "Sacramento Kings": "SAC",
    "San Antonio Spurs": "SAS",
    "Seattle SuperSonics": "SEA",
    "Toronto Raptors": "TOR",
    "Utah Jazz": "UTA",
    "Vancouver Grizzlies": "VAN",
    "Washington Wizards": "WAS"
}

def normalize_abbr(abbr):
    return abbr.upper()

def build_team_mapping(soup, season):
    mapping = {}

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if f"/teams/" in href and f"/{season}.html" in href:
            parts = href.split("/")

            if len(parts) > 3:
                code = normalize_abbr(parts[2])
                name = a.text.strip()

                if len(code) == 3 and name:
                    mapping[name] = code

    return mapping

def get_teams_for_season(season):
    url = f"https://www.basketball-reference.com/leagues/NBA_{season}.html"
    print(f"\nBuscando times de {season}...")

    try:
        response = scraper.get(url)
        if response.status_code != 200:
            print(f"Falha ao obter times de {season}")
            return []
    except Exception as e:
        print(f"Erro ao buscar times: {e}")
        return []

    html = response.text.replace("<!--", "").replace("-->", "")
    soup = BeautifulSoup(html, "lxml")

    mapping = build_team_mapping(soup, season)

    #caso não ache automaticamente
    table = soup.find("table", id="per_game-team")
    if table is not None:
        df = pd.read_html(str(table))[0]

        for team_name in df["Team"].dropna().unique():
            if "League" in team_name:
                continue

            if team_name not in mapping:
                abbr = TEAM_NAME_TO_ABBR.get(team_name)

                if abbr:
                    mapping[team_name] = abbr
                else:
                    print(f"Não mapeado: {team_name}")

    teams = sorted(set(mapping.values()))

    print(f"Times encontrados em {season}: {teams}")
    print(f"Total: {len(teams)}")

    return teams

#principal
for season in range(START_SEASON, END_SEASON + 1):

    teams = get_teams_for_season(season)

    if not teams:
        print(f"Nenhum time encontrado para {season}")
        continue

    for team in teams:

        url = f"https://www.basketball-reference.com/teams/{team}/{season}_games.html"
        print(f"Baixando {team} {season}")

        try:
            response = scraper.get(url)

            if response.status_code == 404:
                print(f"Não existe: {team} {season}")
                continue

            response.raise_for_status()

        except Exception as e:
            print(f"Erro ao baixar {team} {season}: {e}")
            time.sleep(random.uniform(6, 8))
            continue

        html = response.text.replace("<!--", "").replace("-->", "")
        soup = BeautifulSoup(html, "lxml")

        dfs = []

        table_regular = soup.find("table", id="games")
        if table_regular is not None:
            df_regular = pd.read_html(str(table_regular))[0]
            df_regular["is_playoff"] = False
            dfs.append(df_regular)

        table_playoff = soup.find("table", id="games_playoffs")
        if table_playoff is not None:
            df_playoff = pd.read_html(str(table_playoff))[0]
            df_playoff["is_playoff"] = True
            dfs.append(df_playoff)

        if not dfs:
            print(f"Nenhuma tabela encontrada para {team} {season}")
            continue

        df = pd.concat(dfs, ignore_index=True)

        df = df[df["Date"] != "Date"]
        df = df.dropna(how="all")

        df["team"] = team
        df["season"] = season

        filepath = os.path.join(BASE_FOLDER, f"{team}_{season}_games.csv")
        df.to_csv(filepath, index=False, encoding="utf-8")

        print(f"Salvo: {filepath}")

        time.sleep(random.uniform(3, 6))

    print(f"Pausa entre temporadas...")
    time.sleep(random.uniform(10, 20))