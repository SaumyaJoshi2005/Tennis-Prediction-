# -*- coding: utf-8 -*-

from src.acquisition.providers.espn_provider import (
    ESPNProvider
)

from src.acquisition.result_loader import (
    ResultLoader
)


def main():

    print(
        "\n=== ESPN RESULT LOADER TEST ==="
    )

    provider = (
        ESPNProvider()
    )

    print(
        "\nHealth Check:"
    )

    print(
        provider.health_check()
    )

    results = (
        provider.get_results()
    )

    print(
        f"\nResults fetched: "
        f"{len(results)}"
    )

    if results:

        print(
            "\nFirst Result:"
        )

        print(
            results[0]
        )

    loader = (
        ResultLoader(
            provider
        )
    )

    try:

        print(
            "\nLoading results..."
        )

        loader.load_results(
            results
        )

        print(
            "\nResult loading complete."
        )

    except Exception as e:

        print(
            f"\nERROR: {e}"
        )

        raise

    finally:

        loader.close()

        print(
            "\nConnections closed."
        )


if __name__ == "__main__":

    main()