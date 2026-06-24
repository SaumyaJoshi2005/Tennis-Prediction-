# -*- coding: utf-8 -*-
"""
Base provider contract for all external tennis data sources.

All providers must return DTOs and must not contain
database logic, prediction logic, or feature engineering.

Examples:
    ATPProvider
    ESPNProvider
    RolandGarrosProvider
    WimbledonProvider
"""

from abc import (
    ABC,
    abstractmethod
)

from datetime import date as Date

from typing import (
    List,
    Optional
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


class TennisProvider(
    ABC
):

    @property
    @abstractmethod
    def provider_name(
        self
    ) -> str:
        """
        Unique provider identifier.

        Examples:
            ATP
            ESPN
            RolandGarros
            Wimbledon
        """
        pass

    @property
    def provider_version(
        self
    ) -> str:
        """
        Optional provider version.

        Example:
            v1
            v2
        """
        return "v1"

    @abstractmethod
    def health_check(
        self
    ) -> bool:
        """
        Verify that the provider is reachable
        and operational.
        """
        pass

    @abstractmethod
    def supports_fixtures(
        self
    ) -> bool:
        pass

    @abstractmethod
    def supports_results(
        self
    ) -> bool:
        pass

    @abstractmethod
    def supports_players(
        self
    ) -> bool:
        pass

    @abstractmethod
    def get_fixtures(
        self,
        tournament: Optional[str] = None,
        date: Optional[Date] = None
    ) -> List[FixtureDTO]:
        """
        Return upcoming fixtures.
        """
        pass

    @abstractmethod
    def get_results(
        self,
        tournament: Optional[str] = None,
        date: Optional[Date] = None
    ) -> List[ResultDTO]:
        """
        Return completed results.
        """
        pass

    @abstractmethod
    def get_player(
        self,
        player_name: str
    ) -> Optional[PlayerDTO]:
        """
        Return metadata for a single player.

        Returns:
            PlayerDTO or None
        """
        pass