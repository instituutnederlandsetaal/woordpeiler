# standard
import os
import csv

# third party
import traceback

# local
from database.insert.datatypes import CSVRow
from database.insert.uploader import Uploader
from database.insert.sql import (
    create_table_data_tmp,
)


class CsvUploader(Uploader):
    """Custom uploader because data_update csv files are different from the blacklab FrequencyTool tsv files"""

    def upload(self):
        try:
            super().insert_rows(self.__get_rows(self.path))
        except Exception as e:
            print("Error in Uploader")
            print(e)
            traceback.print_exc()
        finally:
            self.cursor.close()

    def __create_tmp_tables(self):
        self.cursor.execute(create_table_data_tmp)

    def __get_rows(self, path: str) -> list[CSVRow]:
        date = os.path.basename(path).split(".")[0]
        rows: list[CSVRow] = []
        with open(path, "r") as file:
            data = csv.DictReader(file)
            for row in data:
                # skip empty lines
                if not "hit text: word" in row:
                    continue
                pos = row["hit text: pos_full"]
                pos_head = self.__pos_to_pos_head(pos)
                rows.append(
                    CSVRow(
                        lemma=row["hit text: lemma"],
                        wordform=row["hit text: word"],
                        pos=pos,
                        poshead=pos_head,
                        date=date,
                        source=row["document: titleLevel2"],
                        language=row["document: languageVariant"],
                        frequency=row["count"],
                    )
                )

        return rows

    def __pos_to_pos_head(self, pos: str) -> str:
        return pos.split("(")[0]

    def insert_rows(self, rows: list[CSVRow]):
        rows = super().__clean_data(rows)
        with self.cursor.copy(
            "COPY data_tmp (wordform, lemma, pos, poshead, time, frequency, source, language) FROM STDIN"
        ) as copy:
            for r in rows:
                copy.write_row(
                    (
                        r.wordform,
                        r.lemma,
                        r.pos,
                        r.poshead,
                        r.date,
                        r.frequency,
                        r.source,
                        r.language,
                    )
                )
