# -*- coding: utf-8 -*-
"""
Created on Wed Jun  3 21:34:37 2026

@author: AUM
"""


from pathlib import Path
import hashlib

from src.scraping.download_rg_pdf import (
    download_pdf
)

PDF_PATH = Path(
    "data/rg_draw.pdf"
)

HASH_PATH = Path(
    "data/rg_draw.hash"
)


def calculate_hash():

    data = PDF_PATH.read_bytes()

    return hashlib.md5(
        data
    ).hexdigest()


def load_previous_hash():

    if not HASH_PATH.exists():

        return None

    return HASH_PATH.read_text().strip()


def save_hash(pdf_hash):

    HASH_PATH.write_text(
        pdf_hash
    )


def main():

    print(
        "Downloading latest RG draw..."
    )

    download_pdf(
        output_path=str(PDF_PATH)
    )

    current_hash = (
        calculate_hash()
    )

    previous_hash = (
        load_previous_hash()
    )

    if current_hash == previous_hash:

        print(
            "No draw changes detected."
        )

        return

    print(
        "Draw updated."
    )

    save_hash(
        current_hash
    )

    from src.scraping.parse_rg_pdf import (extract_players)

    players = extract_players(str(PDF_PATH))

    print(f"Players found: {len(players)}")

    print(
        "TODO: load fixtures"
    )

    print(
        "TODO: generate predictions"
    )


if __name__ == "__main__":
    main()