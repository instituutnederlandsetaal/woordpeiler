# standard
import os
import csv

# third party
import traceback

# local
from database.insert.datatypes import CSVRow
from database.insert.uploader import Uploader


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
                        medium="newspaper",
                        language=row["document: languageVariant"],
                        frequency=row["count"],
                    )
                )

        return rows

    def __pos_to_pos_head(self, pos: str) -> str:
        return pos.split("(")[0]
