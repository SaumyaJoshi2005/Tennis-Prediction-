# src/acquisition/providers/espn_provider.py

import requests

from datetime import (
datetime
)

from src.acquisition.providers.base_provider import (
TennisProvider
)

from src.acquisition.models.fixtures_dto import (
FixtureDTO
)

from src.acquisition.models.result_dto import (
ResultDTO
)

from src.acquisition.models.player_dto import (
    PlayerDTO
)
class ESPNProvider(
        TennisProvider
        ):

    SCOREBOARD_URL = (
    "https://site.api.espn.com/apis/site/v2/"
    "sports/tennis/atp/scoreboard"
)

    @property
    def provider_name(self) -> str:
        return "ESPN"

    def health_check(self) -> bool:
        try:
            response = requests.get(
                self.SCOREBOARD_URL,
                timeout=10
                )
            return (response.status_code== 200)
        except Exception:
            return False

    def supports_fixtures(self) -> bool:
        return True
    
    def supports_results(self) -> bool:
        return True

    def supports_players(self) -> bool:
        return False

    def _load_scoreboard(self):

        response = requests.get(self.SCOREBOARD_URL,timeout=30)

        response.raise_for_status()

        return response.json()

    def get_fixtures(self,tournament=None,date=None):

        fixtures = []
    
        data = self._load_scoreboard()
    
        for event in data.get(
            "events",
            []
        ):
    
            tournament_name = (
                event.get(
                    "name"
                )
            )
    
            for grouping in event.get(
                "groupings",
                []
            ):
                if grouping.get("grouping",{}).get(
    "displayName"
) != "Men's Singles":
                    continue
                for competition in grouping.get(
                    "competitions",
                    []
                ):
    
                    state = (
                        competition
                        .get(
                            "status",
                            {}
                        )
                        .get(
                            "type",
                            {}
                        )
                        .get(
                            "state"
                        )
                    )
    
                    if state != "pre":
                        continue
    
                    competitors = (
                        competition.get(
                            "competitors",
                            []
                        )
                    )
    
                    if len(
                        competitors
                    ) != 2:
                        continue
    
                    if (
                        "athlete"
                        not in competitors[0]
                    ):
                        continue
    
                    if (
                        "athlete"
                        not in competitors[1]
                    ):
                        continue
    
                    player_a = (
                        competitors[0]
                        ["athlete"]
                        ["fullName"]
                    )
    
                    player_b = (
                        competitors[1]
                        ["athlete"]
                        ["fullName"]
                    )
    
                    round_name = (
                        competition
                        .get(
                            "round",
                            {}
                        )
                        .get(
                            "displayName"
                        )
                    )
    
                    match_time = (
                        datetime
                        .fromisoformat(
                            competition[
                                "date"
                            ]
                            .replace(
                                "Z",
                                "+00:00"
                            )
                        )
                    )
    
                    fixtures.append(
    
                        FixtureDTO(
    
                            player_a=player_a,
    
                            player_b=player_b,
    
                            tournament=tournament_name,
    
                            round=round_name,
    
                            match_time=match_time,
    
                            source="ESPN",
    
                            source_id=str(
                                competition[
                                    "id"
                                ]
                            )
                        )
                    )
    
        return fixtures

    def get_results(self,tournament=None,date=None):
        results = []
        data = self._load_scoreboard()
        for event in data.get("events",[]):
            tournament_name = (event.get("name"))
            print(f"Tournamnet: {tournament_name}")
            for grouping in event.get("groupings",[]):
                for competition in grouping.get("competitions",[]):

                    state = (
                        competition
                        ["status"]
                        ["type"]
                        ["state"]
                        )

                    if state != "post":
                        continue

                    competitors = competition.get("competitors",[])

                    if len(competitors) != 2:
                        continue
                    
                    if "athlete" not in competitors[0]:
                        continue
                    
                    if "athlete" not in competitors[1]:
                        continue

                    winner = None
                    loser = None
                    for competitor in competitors:
                        if competitor.get("winner"):
                            winner = (
                                competitor
                                ["athlete"]
                                ["fullName"]
                                )

                        else:
                            loser = (competitor["athlete"]["fullName"])

                    round_name = (
                        competition
                        .get(
                            "round",
                            {}
                            )
                        .get(
                            "displayName"
                            )
                        )

                    match_date = (
                        datetime
                        .fromisoformat(
                            competition[
                                "date"
                                ]
                            .replace(
                                "Z",
                                "+00:00"
                                )
                            )
                        .date()
                        )
                    
                    results.append(
                        
                        ResultDTO(
                            
                            winner=winner,
                            
                            loser=loser,
                            
                            tournament=tournament_name,

                            round=round_name,

                            match_date=match_date,

                            source="ESPN",

                            source_id=str(
                                competition[
                                    "id"
                                    ]
                                )
                            )
                        )

        return results

    def get_player(
    self,
    player_name: str
):

        data = self._load_scoreboard()
    
        target = (
            player_name
            .strip()
            .lower()
        )
    
        for event in data.get(
            "events",
            []
        ):
    
            for grouping in event.get(
                "groupings",
                []
            ):
    
                for competition in grouping.get(
                    "competitions",
                    []
                ):
    
                    for competitor in competition.get(
                        "competitors",
                        []
                    ):
    
                        athlete = (
                            competitor.get(
                                "athlete"
                            )
                        )
    
                        if athlete is None:
                            continue
    
                        full_name = (
                            athlete.get(
                                "fullName"
                            )
                        )
    
                        if not full_name:
                            continue
    
                        if (
                            full_name
                            .strip()
                            .lower()
                            != target
                        ):
                            continue
    
                        country = None
    
                        if athlete.get(
                            "flag"
                        ):
    
                            country = (
                                athlete
                                ["flag"]
                                .get(
                                    "alt"
                                )
                            )
    
                        return PlayerDTO(
    
                            name=full_name,
    
                            country=country,
    
                            ranking=None,
    
                            height_cm=None,
    
                            birth_date=None,
    
                            hand=None,
    
                            source="ESPN"
                        )
    
        return None
        
