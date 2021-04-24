import argparse
import json
import os

from studosi.materijali.subject import SubjectMeta

parser = argparse.ArgumentParser()

# region IO
io_group = parser.add_argument_group("IO")

io_group.add_argument(
    "--path",
    type=str,
    default="meta.json",
    help="The path where to save the meta file.",
)

# endregion

# region Subject
SubjectMeta.decorate_parser(
    parser=parser,
    group_name="subject",
)

# endregion


def main():
    args = parser.parse_args()
    meta = SubjectMeta(config=SubjectMeta.args_to_config(args=args))

    folder = os.path.abspath(os.path.dirname(args.path))

    if not os.path.exists(folder):
        os.makedirs(folder)

    with open(args.path, mode="w+", encoding="utf8", errors="replace") as f:
        f.write(meta.dumps())


if __name__ == "__main__":
    main()
