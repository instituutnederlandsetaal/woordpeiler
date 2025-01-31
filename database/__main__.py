# standard
import sys

# local
import database.primary as primary
import database.secondary as secondary
import database.trends as trends
from database.util.timer import timer


def initialize(folder: str, config_name: str, ngram: int) -> None:
    word_path = f"{folder}/{config_name}_word_lookup.tsv.gz"
    lemma_path = f"{folder}/{config_name}_lemma_lookup.tsv.gz"
    pos_path = f"{folder}/{config_name}_pos_full_lookup.tsv.gz"
    freq_path = f"{folder}/{config_name}.tsv.gz"

    # primary.initialize(
    #     freq_path=freq_path,
    #     ngram=ngram,
    #     word_path=word_path,
    #     lemma_path=lemma_path,
    #     pos_path=pos_path,
    # )
    # if ngram == 1:
    #     secondary.initialize()

    trends.initialize(ngram)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python -m database [folder] [config_name] [ngram]")
        exit()

    with timer("Initializing database"):
        initialize(folder=sys.argv[1], config_name=sys.argv[2], ngram=int(sys.argv[3]))
