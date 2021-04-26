import argparse
from typing import Optional


def decorate_parser_io(
    parser: argparse.ArgumentParser,
    group_name: Optional[str] = "IO",
    group_description: Optional[str] = None,
    prefix: Optional[str] = None,
    suffix: Optional[str] = None,
    root_folder_argname: Optional[str] = "root_folder",
    folder_name_argname: Optional[str] = "folder_name",
    file_name_argname: Optional[str] = "file_name",
):
    if group_name is None:
        group = parser
    else:
        group = parser.add_argument_group(group_name, group_description)

    if prefix is None:
        prefix = ""
    if suffix is None:
        suffix = ""

    def get_full_argname(argname):
        return f"--{prefix}{argname}{suffix}"

    if root_folder_argname is not None:
        group.add_argument(
            get_full_argname(root_folder_argname),
            type=str,
            default=None,
            help="The root materijali folder",
        )

    if folder_name_argname is not None:
        group.add_argument(
            get_full_argname(folder_name_argname),
            type=str,
            default=None,
            help="The name of the folder where the meta file will be saved",
        )

    if file_name_argname is not None:
        group.add_argument(
            get_full_argname(file_name_argname),
            type=str,
            default=None,
            help="The name of the meta file that will be saved",
        )

    return group
