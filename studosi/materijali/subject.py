import argparse
import copy
import json
from typing import Any, Dict, Iterable, Iterator, List, Optional, Set, Tuple

from unidecode import unidecode

from studosi.materijali.exceptions import AbbreviationCollision
from studosi.constants.materijali import subject as subject_constants
from studosi.utils.json_utils import serialize_sets


class Subject:
    programs: Dict[str, str] = {
        "_": "Nevezano za program",
        "fer1": "FER 1",
        "fer2": "FER 2",
        "fer3": "FER 3",
    }

    studies: Dict[str, str] = {
        "_": "Nevezano za studij",
        "preddiplomski": "preddiplomski",
        "diplomski": "diplomski",
        "doktorski": "doktorski",
        "specijalistcki": "specijalistički",
    }

    courses: Dict[str, str] = {
        "_": "Nevezano za smjer",
        "eiit": "Elektrotehnika i informacijska tehnologija",
        "iikt": "Informacijska i komunikacijska tehnologija",
        "rac": "Računarstvo",
    }

    modules: Dict[str, str] = {
        "_": "Nevezano za modul",
        # FER2 - EIIT
        "aut": "Automatika",
        "esit": "Elektrotehnički sustavi i tehnologija",
        "eleenea": "Elektroenergetika",
        "eiri": "Elektroničko i računalno inženjerstvo",
        "ele": "Elektronika",
        # FER3 - EIIT
        "eia": "Elektrostrojarstvo i automatizacija",
        "aie": "Audiotehnologije i elektroakustika",
        # FER2 - IIKT
        "obrinf": "Obradba informacija",
        "tii": "Telekomunikacije i informatika",
        "bkt": "Bežične komunikacijske tehnologije",
        # FER3 - IIKT
        "air": "Automatika i robotika",
        "kist": "Komunikacijske i svemirske tehnologije",
        "iiki": "Informacijsko i komunikacijsko inženjerstvo",
        # FER2 - RAC
        "piiis": "Programsko inženjerstvo i informacijski sustavi",
        "racinz": "Računalno inženjerstvo",
        "raczna": "Računalna znanost",
        # FER3 - RAC
        "zop": "Znanost o podatcima",
        "zom": "Znanost o mrežama",
        "rmui": "Računalno modeliranje u inženjerstvu",
    }

    @staticmethod
    def semester(number: int):
        return f"{number} semestar"

    groups = {
        # Preddiplomski
        "obavezni": "Obavezni predmeti",
        "transverzalni": "Transverzalni predmeti",
        "za_iznimno_uspjesne_studente": "Predmeti za iznimno uspješne studente",
        "vjestine": "Vještine",
        "izborni": "Izborni predmeti",
        # Diplomski
        "teorijski_profila": "Teorijski predmeti profila",
        "specijalizacije_profila": "Predmeti specijalizacije profila",
        "matematike_fizike_prirodoslovlja": (
            "Predmeti matematike, fizike i prirodoslovlja"
        ),
        "humanisticki_drustveni": "Humanistički ili društveni predmeti",
        "strucna_praksa": "Stručna praksa",
        "preporuceni_izborni": "Preporučeni izborni predmeti",
    }

    @staticmethod
    def get_abbreviation(
        name: str,
        prefix: Optional[str] = None,
        suffix: Optional[str] = None,
        existing_abbreviations: Optional[Iterable[str]] = None,
        return_on_fail: bool = False,
    ):
        prefix = [] if prefix is None else [f"{prefix}-"]
        suffix = [] if suffix is None else [f"-{suffix}"]

        def get_suggestion(tokens: List[str]):
            return "".join(prefix + tokens + suffix)

        tokens = subject_constants.WHITESPACE_REGEX.split(name)
        normalized_tokens = [unidecode(token) for token in tokens]

        word_matches = [
            subject_constants.UNICODE_ALPHA_REGEX.fullmatch(x)
            for x in normalized_tokens
        ]
        word_tokens = [match.group() for match in word_matches if match is not None]

        if len(word_tokens) < 3:
            abbreviation_matches = [
                subject_constants.SHORT_ABBREVIATION_TOKEN_REGEX.match(token)
                for token in normalized_tokens
            ]
        else:
            abbreviation_matches = [
                subject_constants.ABBREVIATION_TOKEN_REGEX.match(token)
                for token in normalized_tokens
            ]

        abbreviation_tokens = [
            str(match.group()).upper()
            for match in abbreviation_matches
            if match is not None
        ]

        current_suggestion = get_suggestion(abbreviation_tokens)

        if existing_abbreviations is not None:
            existing = set(existing_abbreviations)

            token_pointer = 0
            letter_pointers = [
                len(abbreviation_token) - 1
                for abbreviation_token in abbreviation_tokens
            ]
            nt_length = len(normalized_tokens)

            while current_suggestion in existing:
                if all(letter_pointer is None for letter_pointer in letter_pointers):
                    if return_on_fail:
                        break

                    raise AbbreviationCollision(name)

                token_pointer = (token_pointer - 1) % nt_length

                token_to_consider = normalized_tokens[token_pointer]

                if letter_pointers[token_pointer] is None:
                    continue
                else:
                    letter_pointers[token_pointer] += 1

                letter_index_to_consider = letter_pointers[token_pointer]

                if letter_index_to_consider < len(token_to_consider):
                    letter_to_append = str(
                        token_to_consider[letter_index_to_consider]
                    ).lower()
                    abbreviation_tokens[token_pointer] += letter_to_append

                    current_suggestion = get_suggestion(abbreviation_tokens)
                else:
                    letter_pointers[token_pointer] = None

        return current_suggestion

    def get_all_abbreviations(
        name: str,
        existing_abbreviations: Optional[Iterable[str]] = None,
    ) -> Iterator[str]:
        if existing_abbreviations is None:
            existing_abbreviations = set()

        existing = set(existing_abbreviations)

        try:
            while True:
                abbreviation = Subject.get_abbreviation(
                    name=name,
                    existing_abbreviations=existing,
                    return_on_fail=False,
                )

                existing.add(abbreviation)

                yield abbreviation
        except AbbreviationCollision:
            return


class SubjectMeta:
    def __init__(self, config: Optional[Dict[str, Any]]):
        self._config = copy.deepcopy(config)

    @staticmethod
    def decorate_parser(
        parser: argparse.ArgumentParser,
        group_name: Optional[str] = None,
        group_desc: Optional[str] = None,
        prefix: Optional[str] = None,
        suffix: Optional[str] = None,
        name_argname: Optional[str] = "name",
        abbreviation_argname: Optional[str] = "abbreviation",
        properties_argname: Optional[str] = "properties",
        links_argname: Optional[str] = "links",
        related_subjects_argname: Optional[str] = "related_subjects",
    ):
        if prefix is None:
            prefix = ""
        if suffix is None:
            suffix = ""

        def get_full_argname(argname: str):
            return f"--{prefix}{argname}{suffix}"

        if group_desc is None:
            group_desc = ""

        group = (
            parser
            if group_name is None
            else parser.add_argument_group(group_name, group_desc)
        )

        if name_argname is not None:
            group.add_argument(
                get_full_argname(name_argname),
                type=str,
                default=None,
                help="The full subject name",
            )

        if abbreviation_argname is not None:
            group.add_argument(
                get_full_argname(abbreviation_argname),
                type=str,
                default=None,
                help="The subject abbreviation",
            )

        if properties_argname is not None:
            group.add_argument(
                get_full_argname(properties_argname),
                type=str,
                nargs="*",
                default=None,
                help=(
                    "The subject properties. List of strings in the format: "
                    "program:study:course:module:semester:group"
                ),
            )

        if links_argname is not None:
            group.add_argument(
                get_full_argname(links_argname),
                type=str,
                nargs="*",
                default=None,
                help=(
                    "The subject links. List of strings in the format: "
                    "`link_identifier:url:description`. The description is optional"
                ),
            )

        if related_subjects_argname is not None:
            group.add_argument(
                get_full_argname(related_subjects_argname),
                type=str,
                nargs="*",
                default=None,
                help=(
                    "Subjects related to this one. List of strings in the format: "
                    "`abbreviation:reason`. The reason is optional"
                ),
            )

        return group

    @staticmethod
    def property_strings_to_dict(
        property_strings: Iterable[str],
    ) -> Dict[str, Dict[str, Dict[str, Dict[str, Dict[int, Set[str]]]]]]:
        to_return = dict()

        for property_string in property_strings:
            (
                program,
                study,
                course,
                module,
                semester,
                group,
            ) = subject_constants.PROPERTY_STRING_DELIMITER_REGEX.split(property_string)

            if program not in to_return:
                to_return[program] = dict()

            program_dict = to_return[program]

            if study not in program_dict:
                program_dict[study] = dict()

            study_dict = program_dict[study]

            if course not in study_dict:
                study_dict[course] = dict()

            course_dict = study_dict[course]

            if module not in course_dict:
                course_dict[module] = dict()

            module_dict = course_dict[module]

            semester = int(semester)

            if semester not in module_dict:
                module_dict[semester] = set()

            module_dict[semester].add(group)

        return to_return

    @staticmethod
    def link_strings_to_dict(link_strings: Iterable[str]) -> Dict[str, Dict[str, str]]:
        to_return = dict()

        for link_string in link_strings:
            (
                link_identifier,
                *link,
            ) = subject_constants.LINK_STRING_DELIMITER_REGEX.split(link_string)

            if link_identifier not in to_return:
                to_return[link_identifier] = dict()

            to_return[link_identifier]["url"] = link[0]

            if len(link) > 1:
                to_return[link_identifier]["description"] = link[1]

        return to_return

    @staticmethod
    def related_subject_string_to_dict(
        related_subject_strings: Iterable[str],
    ) -> Dict[str, Dict[str, str]]:
        to_return = dict()

        for related_subject_string in related_subject_strings:
            related_subject = (
                subject_constants.RELATED_SUBJECT_STRING_DELIMITER_REGEX.split(
                    related_subject_string
                )
            )
            abbreviation = related_subject[0]

            if abbreviation not in to_return:
                to_return[abbreviation] = dict()

            if len(related_subject) > 1:
                to_return[abbreviation]["reason"] = related_subject[1]

        return to_return

    @staticmethod
    def args_to_config(
        args,
        name_argname: Optional[str] = "name",
        abbreviation_argname: Optional[str] = "abbreviation",
        properties_argname: Optional[str] = "properties",
        links_argname: Optional[str] = "links",
        related_subjects_argname: Optional[str] = "related_subjects",
    ):
        args_dict = vars(args)
        config = dict()

        if name_argname is not None and args_dict.get(name_argname) is not None:
            config[name_argname] = args_dict[name_argname]

        if (
            abbreviation_argname is not None
            and args_dict.get(abbreviation_argname) is not None
        ):
            config[abbreviation_argname] = args_dict[abbreviation_argname]

        if (
            properties_argname is not None
            and args_dict.get(properties_argname) is not None
        ):
            config[properties_argname] = SubjectMeta.property_strings_to_dict(
                args_dict[properties_argname]
            )

        if links_argname is not None and args_dict.get(links_argname) is not None:
            config[links_argname] = SubjectMeta.link_strings_to_dict(
                args_dict[links_argname]
            )

        if (
            related_subjects_argname is not None
            and args_dict.get(related_subjects_argname) is not None
        ):
            config[
                related_subjects_argname
            ] = SubjectMeta.related_subject_string_to_dict(
                args_dict[related_subjects_argname]
            )

        return config

    @property
    def config(self) -> Dict[str, Any]:
        return copy.deepcopy(self._config)

    @property
    def name(self) -> Optional[str]:
        return self._config.get("name")

    @property
    def abbreviation(self) -> Optional[str]:
        return self._config.get("abbreviation")

    @property
    def properties(
        self,
    ) -> Optional[Dict[str, Dict[str, Dict[str, Dict[str, Dict[int, List[str]]]]]]]:
        return self._config.get("properties")

    @property
    def links(self) -> Optional[Dict[str, Tuple[str, str]]]:
        return self._config.get("links")

    @property
    def related_subjects(self) -> Optional[Dict[str, str]]:
        return self._config.get("related_subjects")

    def dumps(self) -> str:
        return json.dumps(
            self.config,
            skipkeys=False,
            ensure_ascii=False,
            check_circular=True,
            allow_nan=False,
            indent=2,
            default=serialize_sets,
            sort_keys=False,
        )
