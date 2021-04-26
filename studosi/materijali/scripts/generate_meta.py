import argparse
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

from studosi.materijali.subject import SubjectMeta


def decorate_io(parser: argparse.ArgumentParser):
    io_group = parser.add_argument_group("IO")

    io_group.add_argument(
        "--root_folder",
        type=str,
        default=None,
        help="The root materijali folder",
    )

    io_group.add_argument(
        "--folder_name",
        type=str,
        default=None,
        help="The folder name where the meta file will be saved",
    )

    io_group.add_argument(
        "--file_name",
        type=str,
        default="meta.json",
        help="The name of the meta file",
    )

    return io_group


def save_meta(
    meta: SubjectMeta,
    root_folder: Optional[Union[Path, str]] = None,
    folder_name: Optional[str] = None,
    file_name: Optional[str] = None,
):
    if root_folder is None:
        print(meta.dumps())
    else:
        root_path = Path(root_folder)

        if folder_name is None:
            if meta.abbreviation is None:
                raise RuntimeError("SubjectMeta abbreviation can't be None")

            folder_name = meta.abbreviation

        save_folder = root_path / folder_name
        save_path = save_folder / file_name

        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        with open(save_path, mode="w+", encoding="utf8", errors="replaces") as f:
            f.write(meta.dumps())


def main():
    parser = argparse.ArgumentParser()

    decorate_io(parser=parser)
    SubjectMeta.decorate_parser(parser=parser, group_name="subject")

    args = parser.parse_args()

    meta = SubjectMeta(config=SubjectMeta.args_to_config(args=args))

    args_dict = vars(args)

    (root_folder, folder_name, file_name) = [
        args_dict.get(x) for x in ("root_folder", "folder_name", "file_name")
    ]

    save_meta(
        meta=meta,
        abbreviation=meta.abbreviation,
        root_folder=root_folder,
        folder_name=folder_name,
        file_name=file_name,
    )


if __name__ == "__main__":
    main()
