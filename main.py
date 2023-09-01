from collections import defaultdict
import numpy as np
import tabula
import requests
from bs4 import BeautifulSoup
from tabulate import tabulate

DIVISIONS = [
    "男甲 1 組",
    "男甲 2 組",
    "男乙 1 組",
    "男乙 2 組",
    "男丙 A 組",
    "男丙 B 組",
    "男丙 C 組",
    "男丙 D 組",
    "女甲 1 組",
    "女甲 2 組",
    "女子乙組",
    "女丙 A 組",
    "女丙 B 組",
]

TYPOS = {"Citysuper": "CITYSUPER", "Akita": "AKITA", "梁球琚": "梁銶琚"}


def get_url() -> str:
    response = requests.get("http://handball.org.hk/competition.htm")
    soup = BeautifulSoup(response.content, "html.parser")
    pdf_link = soup.select_one(
        "#table15 > tr:first-child > td:nth-child(2) > table > tr:nth-child(29) > td:first-child > font:nth-child(2) > font:nth-child(2) > a"
    )["href"]
    return f"http://handball.org.hk/{pdf_link}"


def get_score(result_str: str) -> tuple[int]:
    score_parts = result_str.split("(")[0].strip()
    return tuple(int(score) for score in score_parts.split(":"))


def get_walkover_team(result_str: str) -> str:
    return result_str.split("棄權")[0].strip()


def get_matches(path: str) -> dict:
    dfs = tabula.read_pdf(path, pages="all")
    matches = []

    for df in dfs:
        df = df.dropna(subset=[df.columns[0]])
        for values in df.values.tolist():
            values = [v for v in values if not isinstance(v, float) or not np.isnan(v)]
            *_, division, home_team, away_team, result_str = values
            if result_str.count(":") != 2 and ("棄權" not in result_str):
                continue
            if "棄權" in result_str:
                walkover_team = get_walkover_team(result_str)
                if walkover_team not in (home_team, away_team):
                    raise ValueError(
                        f"{walkover_team} does not match either {home_team} or {away_team}"
                    )
                home_score, away_score = (
                    (0, 12) if walkover_team == home_team else (12, 0)
                )
            else:
                walkover_team = None
                home_score, away_score = get_score(result_str)
            matches.append(
                {
                    "id": int(values[0]),
                    "division": division,
                    "home_team": TYPOS.get(home_team, home_team),
                    "away_team": TYPOS.get(away_team, away_team),
                    "home_score": home_score,
                    "away_score": away_score,
                    "walkover": walkover_team,
                }
            )

    return matches


def calculate_points(home: int, away: int) -> tuple[int]:
    if home > away:
        return 2, 0
    elif home == away:
        return 1, 1
    return 0, 2


def get_tables(matches: dict) -> dict:
    tables = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    for match in matches:
        division = match["division"]
        home_team = match["home_team"]
        away_team = match["away_team"]
        home_score = match["home_score"]
        away_score = match["away_score"]
        home_points, away_points = calculate_points(home_score, away_score)

        tables[division][home_team]["Matches Played"] += 1
        tables[division][away_team]["Matches Played"] += 1
        tables[division][home_team]["Goal Difference"] += home_score - away_score
        tables[division][away_team]["Goal Difference"] += away_score - home_score
        tables[division][home_team]["Points"] += home_points
        tables[division][away_team]["Points"] += away_points

        if walkover := match["walkover"]:
            tables[division][walkover]["Points"] -= 1

    return tables


def print_table(table: dict) -> None:
    teams = [{"Team": team, **stat} for team, stat in table.items()]
    teams = sorted(
        teams, key=lambda x: (x["Points"], x["Goal Difference"]), reverse=True
    )
    print(
        tabulate(teams, headers="keys"),
    )


def main():
    url = get_url()
    matches = get_matches(url)
    tables = get_tables(matches)
    for division in DIVISIONS:
        print(division)
        print_table(tables[division])
        print()


if __name__ == "__main__":
    main()
