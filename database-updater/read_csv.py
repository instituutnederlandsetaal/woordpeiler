import csv
import os


def pos_to_pos_head(pos: str) -> str:
    return pos.split("(")[0]


def get_wordforms(path="data/20240601.csv"):
    date = os.path.basename(path).split(".")[0]
    wordforms = []
    with open(path, "r") as file:
        data = csv.DictReader(file)
        for row in data:
            # skip empty lines
            if not "hit text: word" in row:
                continue
            pos = row["hit text: pos_full"]
            pos_head = pos_to_pos_head(pos)
            wordforms.append(
                (
                    date,
                    row["hit text: word"],
                    row["hit text: lemma"],
                    pos,
                    pos_head,
                    row["count"],
                    row["document: titleLevel2"],
                )
            )

    return set(wordforms)
