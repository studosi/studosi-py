import argparse
import os
from pathlib import Path
import sys
from typing import Any, Dict

from studosi.materijali.scripts.generate_materijali.parsing import decorate_parser_io
from studosi.materijali.subject import SubjectMeta
from studosi.materijali.scripts.generate_meta import save_meta

config = {
    "name": "Ime predmeta",
    "abbreviation": "IMEPRE",
    "properties": {
        "program": {
            "studij": {
                "smjer": {
                    "modul": {
                        "semestar": {
                            "grupa_predmeta",
                        }
                    }
                }
            }
        }
    },
    "links": {
        "identifikator": {
            "url": "https://www.google.com",
            "description": "Opis poveznice",
        },
    },
    "related_subjects": {
        "kratica_predmeta": {
            "reason": "Razlog zašto je kratica dodana",
        },
    },
}


def main():
    parser = argparse.ArgumentParser()

    decorate_parser_io(parser=parser)

    args = parser.parse_args()
    args_dict = vars(args)

    meta = SubjectMeta(config=config)

    root_folder = args_dict.get("root_folder", os.path.abspath("./"))
    folder_name = args_dict.get("folder_name", meta.abbreviation)
    file_name = args_dict.get("file_name", "meta.json")

    validation_result = SubjectMeta.is_valid(meta.config)

    if validation_result is not None:
        print(validation_result, file=sys.stderr)

    save_meta(
        meta=meta, root_folder=root_folder, folder_name=folder_name, file_name=file_name
    )


if __name__ == "__main__":
    main()
