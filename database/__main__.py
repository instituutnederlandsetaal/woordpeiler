# standard
import sys

# local
import database.primary as primary
import database.trends as trends
from database.util.timer import timer
from database.util.query import vacuum_analyze


def initialize(folder: str, config_name: str, ngram: int) -> None:
    word_path = f"{folder}/{config_name}_word.tsv"
    lemma_path = f"{folder}/{config_name}_lemma.tsv"
    pos_path = f"{folder}/{config_name}_pos_full.tsv"
    words_path = f"{folder}/{config_name}_annotations.tsv"
    source_path = f"{folder}/{config_name}_metadata.tsv"
    size_path = f"{folder}/{config_name}_size.tsv"
    freq_path = f"{folder}/{config_name}.tsv"

    primary.initialize(
        freq_path=freq_path,
        ngram=ngram,
        word_path=word_path,
        lemma_path=lemma_path,
        pos_path=pos_path,
        source_path=source_path,
        words_path=words_path,
        size_path=size_path,
    )

    trends.initialize(ngram)

    vacuum_analyze()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python -m database [folder] [config_name] [ngram]")
        exit()

    with timer("Initializing database"):
        initialize(folder=sys.argv[1], config_name=sys.argv[2], ngram=int(sys.argv[3]))
        print("Done!")
