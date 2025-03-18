# standard
import tempfile
import os
import re
from pathlib import Path
import sys

# third party
from dotenv import load_dotenv

# local
from database.util.timer import timer

load_dotenv()

MOLEX_PASSWORD = os.getenv("MOLEX_PASSWORD")
MOLEX_HOST = os.getenv("MOLEX_HOST")


def preprocess(chn_wordforms: str) -> str:
    tmp_dir = tempfile.mkdtemp()
    molex_path = os.path.join(tmp_dir, "molex.txt")
    exolex_path = os.path.join(tmp_dir, "exolex.tsv")

    # dump
    os.system(f"""
        PGPASSWORD={MOLEX_PASSWORD} psql -h{MOLEX_HOST} -Udba -dgig_pro -c"SELECT DISTINCT wordform_lowercase FROM data.wordforms" -t -A -o {molex_path} 
    """)

    # dos2unix
    os.system(f"""
        dos2unix {molex_path} {chn_wordforms}
    """)

    expand_molex(molex_path)

    with timer("Creating exolex"):
        # create exolex
        os.system(f"""
            awk 'NR==FNR {{molex[$1]; next}} !($2 in molex)' {molex_path} {chn_wordforms} > {exolex_path}
        """)

    # gzip
    with timer("Gzipping"):
        os.system(f"""
            gzip {exolex_path}
        """)
    exolex_path += ".gz"

    return exolex_path


def expand_molex(molex_path: str):
    tmp_dir = tempfile.mkdtemp()
    tmp_file_path = os.path.join(tmp_dir, "tmp.txt")

    # remove and split spaces
    os.system(f"""
        tr -d ' ' < {molex_path} > {tmp_file_path} && \
        tr ' ' '\n' < {molex_path} >> {tmp_file_path} && \
        mv {tmp_file_path} {molex_path}
    """)

    # sort uniq
    os.system(f"""
        sort -u {molex_path} -o {molex_path}
    """)

    with timer("Creating substitutions"):
        apply_substitutions(molex_path, tmp_file_path)

    # unicode normalize
    # NOTE: needs to be after substitutions to support substituting é
    os.system(f"""
        iconv -f utf-8 -t ascii//TRANSLIT {molex_path} -o {tmp_file_path} && \
        mv {tmp_file_path} {molex_path}
    """)

    # sort uniq
    os.system(f"""
        sort -u {molex_path} -o {molex_path}
    """)


def apply_substitutions(molex_path: str, tmp_file_path: str):
    subs: list[tuple[str, str]] = [
        ("c(?=[^hei])", "k"),  # product -> produkt
        ("ch(?=[^ei])", "k"),  # christen -> kristen
        ("qu", "kw"),  # consequent -> consekwent
        ("th", "t"),  # thema -> tema
        ("euz", "eus"),  # luxueuze -> luxeuse
        ("s(?=[aeiouy])", "z"),  # organisatie -> organizatie
        ("ks", "x"),  # seksueel -> sexueel
        ("x", "ks"),  # exemplaar -> eksemplaar
        ("cc(?=[ei])", "ks"),  # succes -> sukses, accijns -> aksijns
        ("cc(?=[^ei])", "kk"),  # accu -> akku
        ("ou", "oe"),  # gouveneur -> goeveneur
        ("'s", "'"),  # foto's -> foto'
        ("-", ""),  # zuid-afrika -> zuidafrika
        ("é", "ee"),  # comité -> comitee
        ("bijzonder", "biezonder"),
        ("eerd$", "eerde"),  # geconsolideerd -> geconsolideerde
    ]
    for patt, sub in subs:
        add_combinatorial_substitutions(
            Path(molex_path), Path(tmp_file_path), patt, sub
        )
        os.system(f"mv {tmp_file_path} {molex_path}")


def add_combinatorial_substitutions(
    input: Path, tmp: Path, patt: str, sub: str
) -> None:
    """
    For each line in the file at @input, finds all occurrences of @patt and combinatorially substitutes them
    with @sub such that all possible combinations of substitutions are created (on a new line per word).
    Also keep the original line.
    Example:
    Substitute c with k in communicatie:
    output: communicatie, kommunicatie, communikatie, kommunikatie
    """
    # compile the pattern
    pattern = re.compile(patt)

    # write to tmp file, overwrite
    with open(tmp, "w") as output_file:
        with open(input, "r") as input_file:
            for line in input_file:
                line = line.strip()
                # write original line
                output_file.write(line + "\n")
                # write all combinatorial substitutions
                matches = list(pattern.finditer(line))
                start_indices = [match.start() for match in matches]
                end_indices = [match.end() for match in matches]
                for i in range(1, 2 ** len(start_indices)):
                    new_line = line
                    shift = 0
                    for j, (start, end) in enumerate(zip(start_indices, end_indices)):
                        if i & (1 << j):
                            new_line = (
                                new_line[: start + shift]
                                + sub
                                + new_line[end + shift :]
                            )
                            shift += len(sub) - (end - start)
                    output_file.write(new_line + "\n")


# create exolex using:
# docker compose exec database psql -U postgres -d woordpeiler -c \
# "SELECT abs_freq, poshead, e.wordform FROM total_counts_1 JOIN words_1 on words_1.id = word_id JOIN exolex e ON e.id = wordform_ids[1] JOIN posses p on p.id = pos_ids[1] \
#  WHERE NOT (pos_ids[1] = ANY (SELECT id FROM posses where poshead = 'nou-p' OR poshead = 'num' OR poshead = 'res' OR poshead = 'punct' OR poshead='__eos__')) ORDER BY abs_freq DESC;" \
# -t -A -F $'\t' | grep -v -P '.*\t.*\t.*[-\./,\(\)].*' > exolex.tsv


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 -m database.exolex.preprocess_exolex [path]")

    # copy so we don't overwrite the original file
    path = sys.argv[1]
    out = path.split(".")[0] + ".sub.txt"
    os.system(f"cp {path} {out}")

    expand_molex(out)
