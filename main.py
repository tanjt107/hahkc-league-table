import numpy as np
import tabula
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
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


def get_url() -> str:
    response = requests.get("http://handball.org.hk/competition.htm")
    soup = BeautifulSoup(response.content, "html.parser")
    pdf_link = soup.select_one(
        "#table15 > tr:first-child > td:nth-child(2) > table > tr:nth-child(29) > td:first-child > font:nth-child(2) > font:nth-child(2) > a"
    )["href"]
    return f"http://handball.org.hk/{pdf_link}"


def get_score(score_str: str) -> tuple[int]:
    score_parts = score_str.split(" (")
    return tuple(int(score) for score in score_parts[0].split(":"))


def get_matches(path: str) -> dict:
    dfs = tabula.read_pdf(path, pages="all")
    matches = []

    for df in dfs:
        df = df.dropna(subset=[df.columns[0]])
        for values in df.values.tolist():
            values: list[str] = [
                v for v in values if not isinstance(v, float) or not np.isnan(v)
            ]
            if values[-1].count(":") != 2:
                continue
            home_team: str = values[-3]
            away_team: str = values[-2]
            home_score, away_score = get_score(values[-1])
            matches.append(
                {
                    "id": int(values[0]),
                    "division": values[-4],
                    "home_team": home_team.upper()
                    if home_team.isalpha()
                    else home_team,
                    "away_team": away_team.upper()
                    if away_team.isalpha()
                    else away_team,
                    "home_score": home_score,
                    "away_score": away_score,
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

        tables[division][home_team]["played"] += 1
        tables[division][away_team]["played"] += 1
        tables[division][home_team]["goal_dif"] += home_score - away_score
        tables[division][away_team]["goal_dif"] += away_score - home_score
        tables[division][home_team]["points"] += home_points
        tables[division][away_team]["points"] += away_points

    return tables


def print_table(table: dict) -> None:
    teams = [{"team": team, **stat} for team, stat in table.items()]
    teams = sorted(teams, key=lambda x: (x["points"], x["goal_dif"]), reverse=True)
    print(
        tabulate(
            teams,
            headers={
                "team": "Team",
                "played": "Matches Played",
                "goal_dif": "Goal Difference",
                "points": "Points",
            },
            tablefmt="github",
        ),
    )


def main():
    # pdf_url = get_url()
    url = "http://handball.org.hk/2_Competition/2018-2019/%e8%81%af%e8%b3%bd/(190)%202018_LAEGUE_TIMETABLE_2020.08.15.pdf"
    matches = get_matches(url)
    tables = get_tables(matches)
    for division in DIVISIONS:
        print(division)
        print_table(tables[division])
        print()


if __name__ == "__main__":
    main()
