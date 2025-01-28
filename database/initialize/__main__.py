# standard
import sys

# local
import database.initialize.primary as primary
from database.util.timer import timer


def initialize(folder: str, config_name: str) -> None:
    word_path = f"{folder}/{config_name}_word_lookup.tsv.gz"
    lemma_path = f"{folder}/{config_name}_lemma_lookup.tsv.gz"
    pos_path = f"{folder}/{config_name}_pos_full_lookup.tsv.gz"
    freq_path = f"{folder}/{config_name}.tsv.gz"

    # initialize primary data tables (wordforms, lemmas, pos, frequencies, sources, words)
    primary.initialize(
        word_path=word_path,
        lemma_path=lemma_path,
        pos_path=pos_path,
        freq_path=freq_path,
    )


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python -m database.initialize [folder] [config_name]")
        exit()

    with timer("Initializing database"):
        initialize(folder=sys.argv[1], config_name=sys.argv[2])
