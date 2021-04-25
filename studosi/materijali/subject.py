import argparse
import copy
import json
import sys
from typing import Any, Dict, Iterable, Iterator, List, Optional, Set, Tuple, Type

from unidecode import unidecode

from studosi.constants import regex as regex_constants
from studosi.materijali.exceptions import AbbreviationCollision
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
        return f"{number}. semestar"

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

        tokens = regex_constants.WHITESPACE_REGEX.split(name)
        normalized_tokens = [unidecode(token) for token in tokens]

        word_matches = [
            regex_constants.UNICODE_ALPHA_REGEX.fullmatch(x) for x in normalized_tokens
        ]
        word_tokens = [match.group() for match in word_matches if match is not None]

        if len(word_tokens) < 3:
            abbreviation_matches = [
                regex_constants.SHORT_ABBREVIATION_TOKEN_REGEX.match(token)
                for token in normalized_tokens
            ]
        else:
            abbreviation_matches = [
                regex_constants.ABBREVIATION_TOKEN_REGEX.match(token)
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
    _default_name_key = "name"
    _default_abbreviation_key = "abbreviation"
    _default_properties_key = "properties"
    _default_links_key = "links"
    _default_related_subjects_key = "related_subjects"

    _links_properties = {
        "url",
        "description",
    }
    _related_subject_properties = {
        "reason",
    }

    _actions_on_wrong_value = {
        "nothing",
        "warn",
        "raise",
    }

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
                    "`link_identifier::url::description`. The description is optional"
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
    ) -> Dict[str, Dict[str, Dict[str, Dict[str, Dict[str, Set[str]]]]]]:
        to_return = dict()

        for property_string in property_strings:
            (
                program,
                study,
                course,
                module,
                semester,
                group,
            ) = regex_constants.PROPERTY_STRING_DELIMITER_REGEX.split(property_string)

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
            ) = regex_constants.LINK_STRING_DELIMITER_REGEX.split(link_string)

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
                regex_constants.RELATED_SUBJECT_STRING_DELIMITER_REGEX.split(
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
        convert_keys: bool = False,
        action_on_wrong_value: str = "warn",
    ):
        if action_on_wrong_value is None:
            action_on_wrong_value = "nothing"

        action_on_wrong_value = str(action_on_wrong_value).lower()

        if action_on_wrong_value not in SubjectMeta._actions_on_wrong_value:
            actions = list(sorted(SubjectMeta._actions_on_wrong_value))
            error_string = (
                ", ".join((f"`{x}`" for x in actions[:-1])) + f" or {actions[-1]}"
            )

            raise KeyError(
                f"SubjectMeta action_on_wrong_value must be one of: {error_string}"
            )

        args_dict = vars(args)
        config = dict()

        if name_argname is not None and args_dict.get(name_argname) is not None:
            config[
                SubjectMeta._default_name_key if convert_keys else name_argname
            ] = args_dict[name_argname]

        if (
            abbreviation_argname is not None
            and args_dict.get(abbreviation_argname) is not None
        ):
            config[
                SubjectMeta._default_abbreviation_key
                if convert_keys
                else abbreviation_argname
            ] = args_dict[abbreviation_argname]

        if (
            properties_argname is not None
            and args_dict.get(properties_argname) is not None
        ):
            config[
                SubjectMeta._default_properties_key
                if convert_keys
                else properties_argname
            ] = SubjectMeta.property_strings_to_dict(args_dict[properties_argname])

        if links_argname is not None and args_dict.get(links_argname) is not None:
            config[
                SubjectMeta._default_links_key if convert_keys else links_argname
            ] = SubjectMeta.link_strings_to_dict(args_dict[links_argname])

        if (
            related_subjects_argname is not None
            and args_dict.get(related_subjects_argname) is not None
        ):
            config[
                SubjectMeta._default_related_subjects_key
                if convert_keys
                else related_subjects_argname
            ] = SubjectMeta.related_subject_string_to_dict(
                args_dict[related_subjects_argname]
            )

        if action_on_wrong_value != "nothing":
            validity_result = SubjectMeta.is_valid(config=config)

            if validity_result is not None:
                if action_on_wrong_value == "warn":
                    print(validity_result, file=sys.stderr)
                elif action_on_wrong_value == "raise":
                    raise RuntimeError(validity_result)

        return config

    # region Properties
    @property
    def config(self) -> Dict[str, Any]:
        return copy.deepcopy(self._config)

    @property
    def name(self) -> Optional[str]:
        return self._config.get(SubjectMeta._default_name_key)

    @property
    def abbreviation(self) -> Optional[str]:
        return self._config.get(SubjectMeta._default_abbreviation_key)

    @property
    def properties(
        self,
    ) -> Optional[Dict[str, Dict[str, Dict[str, Dict[str, Dict[str, List[str]]]]]]]:
        return self._config.get(SubjectMeta._default_properties_key)

    @property
    def links(self) -> Optional[Dict[str, Dict[str, str]]]:
        return self._config.get(SubjectMeta._default_links_key)

    @property
    def related_subjects(self) -> Optional[Dict[str, str]]:
        return self._config.get(SubjectMeta._default_related_subjects_key)

    # endregion

    # region Validation
    @staticmethod
    def validate_name(name: str):
        if name is None:
            raise TypeError("SubjectMeta name mustn't be None")

        try:
            name = str(name)
        except TypeError:
            raise TypeError("SubjectMeta name should be castable to string")

        if len(name) == 0:
            raise ValueError("SubjectMeta name shouldn't be empty")

    @staticmethod
    def validate_abbreviation(abbreviation: str):
        if abbreviation is None:
            raise TypeError("SubjectMeta abbreviation mustn't be None")

        try:
            abbreviation = str(abbreviation)
        except TypeError:
            raise TypeError("SubjectMeta abbreviation should be castable to string")

        if len(abbreviation) == 0:
            raise ValueError("SubjectMeta abbreviation shouldn't be empty")

        if regex_constants.WHITESPACE_REGEX.search(abbreviation) is not None:
            raise ValueError(
                "SubjectMeta abbreviation shouldn't contain any whitespace"
            )

    @staticmethod
    def validate_properties(
        properties: Dict[str, Dict[str, Dict[str, Dict[str, Dict[str, List[str]]]]]]
    ):
        for program in properties:
            if program is None:
                raise TypeError("SubjectMeta properties program can't be None")

            if program not in Subject.programs:
                programs = list(sorted(Subject.programs))
                error_string = (
                    ", ".join((f"`{x}`" for x in programs[:-1])) + f" or {programs[-1]}"
                )

                raise KeyError(
                    f"SubjectMeta properties program must be one of: {error_string}"
                )

            program_dict = properties[program]

            for study in program_dict:
                if study is None:
                    raise TypeError("SubjectMeta properties study can't be None")

                if study not in Subject.studies:
                    studies = list(sorted(Subject.studies))
                    error_string = (
                        ", ".join((f"`{x}`" for x in studies[:-1]))
                        + f" or {studies[-1]}"
                    )

                    raise KeyError(
                        f"SubjectMeta properties study must be one of: {error_string}"
                    )

                study_dict = program_dict[study]

                for course in study_dict:
                    if course is None:
                        raise TypeError("SubjectMeta properties course can't be None")

                    if course not in Subject.courses:
                        courses = list(sorted(Subject.courses))
                        error_string = (
                            ", ".join((f"`{x}`" for x in courses[:-1]))
                            + f" or {courses[-1]}"
                        )

                        raise KeyError(
                            (
                                "SubjectMeta properties course must be one of: "
                                f"{error_string}"
                            )
                        )

                    course_dict = study_dict[course]

                    for module in course_dict:
                        if module is None:
                            raise TypeError(
                                "SubjectMeta properties module can't be None"
                            )

                        if module not in Subject.modules:
                            modules = list(sorted(Subject.modules))
                            error_string = (
                                ", ".join((f"`{x}`" for x in modules[:-1]))
                                + f" or {modules[-1]}"
                            )

                            raise KeyError(
                                (
                                    "SubjectMeta properties module must be one of: "
                                    f"{error_string}"
                                )
                            )

                        module_dict = course_dict[module]

                        for semester in module_dict:
                            if semester is None:
                                raise TypeError(
                                    "SubjectMeta properties semester can't be None"
                                )

                            try:
                                int(semester)
                            except TypeError:
                                raise TypeError("Semester must be convertible to int")

                            groups = module_dict[semester]

                            for group in groups:
                                if group is None:
                                    raise TypeError(
                                        "SubjectMeta properties group can't be None"
                                    )

                                if group not in Subject.groups:
                                    groups = list(sorted(Subject.groups))
                                    error_string = (
                                        ", ".join((f"`{x}`" for x in groups[:-1]))
                                        + f" or {groups[-1]}"
                                    )

                                    raise KeyError(
                                        (
                                            "SubjectMeta properties group must be one "
                                            f"of: {error_string}"
                                        )
                                    )

    @staticmethod
    def validate_links(links: Dict[str, Dict[str, str]]):
        for link_identifier in links:
            if link_identifier is None:
                raise TypeError("SubjectMeta links link_identifier can't be None")

            for property_key, property_value in links[link_identifier].items():
                if property_key not in SubjectMeta._links_properties:
                    keys = list(sorted(SubjectMeta._links_properties))
                    error_string = (
                        ", ".join((f"`{x}`" for x in keys[:-1])) + f" or {keys[-1]}"
                    )

                    raise KeyError(
                        f"SubjectMeta links property key must be one of: {error_string}"
                    )

                if property_value is None:
                    raise TypeError("SubjectMeta links property value can't be None")

    @staticmethod
    def validate_related_subjects(related_subjects: Dict[str, Dict[str, str]]):
        for abbreviation in related_subjects:
            SubjectMeta.validate_abbreviation(abbreviation)

            for property_key, property_value in related_subjects[abbreviation].items():
                if property_key not in SubjectMeta._related_subject_properties:
                    keys = list(sorted(SubjectMeta._related_subject_properties))
                    error_string = (
                        ", ".join((f"`{x}`" for x in keys[:-1])) + f" or {keys[-1]}"
                    )

                    raise KeyError(
                        (
                            f"SubjectMeta related_subjects property key must be one "
                            f"of: {error_string}"
                        )
                    )

                if property_value is None:
                    raise TypeError(
                        "SubjectMeta related_subjects property value can't be None"
                    )

    @staticmethod
    def is_valid(config: Dict[str, Any]):
        failed = dict()

        for function, key in zip(
            (
                SubjectMeta.validate_name,
                SubjectMeta.validate_abbreviation,
                SubjectMeta.validate_properties,
                SubjectMeta.validate_links,
                SubjectMeta.validate_related_subjects,
            ),
            (
                SubjectMeta._default_name_key,
                SubjectMeta._default_abbreviation_key,
                SubjectMeta._default_properties_key,
                SubjectMeta._default_links_key,
                SubjectMeta._default_related_subjects_key,
            ),
        ):
            try:
                function(config[key])
            except Exception as e:
                failed[key] = str(e)

        if len(failed) != 0:
            failed_tuple = sorted(
                ((key, value) for key, value in failed.items()),
                key=lambda x: (x[0], len(x[1])),
            )
            failed_string = "\n\t".join(
                f"{key}: {value}" for key, value in failed_tuple
            )

            return f"Validity checks failed for:\n\t{failed_string}"

        return

    # endregion

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
