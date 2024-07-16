import csv

# curl 'http://svotmc10.ivdnt.loc:8080/blacklab-server/chn-intern/hits?patt=%5B%5D&filter=%2BpubDate_from%3A%2220240601%22%20%2Bmedium%3Anewspaper&group=field%3AtitleLevel2%3Ai%2Chit%3Alemma%3Ai%2Chit%3Aword%3Ai%2Chit%3Apos_full%3Ai&outputformat=csv&csvsummary=no&csvsepline=no' -o outfile.csv

# document: titleLevel2,hit text: lemma,hit text: word,hit text: pos_full,count,numberOfDocs,subcorpusSize.documents,subcorpusSize.numberOfTokens


# Read hits.csv
def get_wordforms(path="20240601.csv"):
    date = path.split(".")[0]
    wordforms = []
    with open(path, "r") as file:
        data = csv.DictReader(file)
        for row in data:
            wordforms.append(
                (
                    date,
                    row["hit text: word"],
                    row["hit text: lemma"],
                    row["hit text: pos_full"],
                    row["count"],
                    row["document: titleLevel2"],
                )
            )

    return set(wordforms)
