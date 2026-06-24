# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 00:55:40 2026

@author: AUM
"""

from typing import List

from src.acquisition.providers.base_provider import (
    TennisProvider
)


class ProviderRegistry:

    def __init__(self):

        self._providers: List[
            TennisProvider
        ] = []

    def register(
        self,
        provider: TennisProvider
    ):

        self._providers.append(
            provider
        )

    def get_all(
        self
    ) -> List[TennisProvider]:

        return self._providers

    def get_fixture_providers(
        self
    ) -> List[TennisProvider]:

        return [
            provider
            for provider in self._providers
            if provider.supports_fixtures()
        ]

    def get_result_providers(
        self
    ) -> List[TennisProvider]:

        return [
            provider
            for provider in self._providers
            if provider.supports_results()
        ]

    def get_player_providers(
        self
    ) -> List[TennisProvider]:

        return [
            provider
            for provider in self._providers
            if provider.supports_players()
        ]

    def get_provider(
        self,
        provider_name: str
    ):

        for provider in self._providers:

            if (
                provider.provider_name
                == provider_name
            ):
                return provider

        return None