# standard
from pathlib import Path
import sys

# local
import database.primary as primary
import database.trends as trends
from database.util.timer import timer
from database.util.query import vacuum_analyze


def initialize(folder: Path, config_name: str, ngram: int) -> None:
    frequency = folder / f"{config_name}.tsv"
    annotations = folder / f"{config_name}_annotations.tsv"
    size = folder / f"{config_name}_size.tsv"
    metadata = folder / f"{config_name}_metadata.tsv"
    word = folder / f"{config_name}_word.tsv"
    lemma = folder / f"{config_name}_lemma.tsv"
    pos = folder / f"{config_name}_pos_full.tsv"

    primary.initialize(ngram, frequency, annotations, size, metadata, word, lemma, pos)
    trends.initialize(ngram)
    vacuum_analyze()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Woordpeiler database initialisation tool.\n")
        print("Usage:\n\tpython -m database [folder] [name] [ngram]\n")
        print("- folder: folder containing output from the Blacklab FrequencyTool.")
        print("\tExample folder contents:")
        print("\t\tunigram_word.tsv")
        print("\t\tunigram_lemma.tsv")
        print("\t\tunigram_pos.tsv")
        print("\t\tunigram_annotations.tsv")
        print("\t\tunigram_metadata.tsv")
        print("\t\tunigram_size.tsv")
        print("\t\tunigram.tsv")
        print("- name: config name as in the Blacklab FrequencyTool. See file names.")
        print("\tExample: unigram")
        print("- ngram: the n-gram size of this config.")
        print("\tExample: 1")
        exit()

    with timer("Initializing database"):
        initialize(
            folder=Path(sys.argv[1]), config_name=sys.argv[2], ngram=int(sys.argv[3])
        )
        print("Done!")
