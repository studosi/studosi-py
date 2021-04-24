import re
import regex

WHITESPACE_PATTERN = r"\s+"
WHITESPACE_REGEX = re.compile(WHITESPACE_PATTERN)

UNICODE_ALPHA_PATTERN = r"\p{L}+"
UNICODE_ALPHA_REGEX = regex.compile(UNICODE_ALPHA_PATTERN)

SHORT_ABBREVIATION_TOKEN_PATTERN = r"[\p{L}\p{N}]{1,3}[\p{Lu}\p{N}]*"
SHORT_ABBREVIATION_TOKEN_REGEX = regex.compile(SHORT_ABBREVIATION_TOKEN_PATTERN)

ABBREVIATION_TOKEN_PATTERN = r"[\p{L}\p{N}][\p{Lu}\p{N}]*"
ABBREVIATION_TOKEN_REGEX = regex.compile(ABBREVIATION_TOKEN_PATTERN)

PROPERTY_STRING_DELIMITER_PATTERN = r"\:"
PROPERTY_STRING_DELIMITER_REGEX = re.compile(PROPERTY_STRING_DELIMITER_PATTERN)

LINK_STRING_DELIMITER_PATTERN = r"\:\:"
LINK_STRING_DELIMITER_REGEX = re.compile(LINK_STRING_DELIMITER_PATTERN)

RELATED_SUBJECT_STRING_DELIMITER_PATTERN = r"\:"
RELATED_SUBJECT_STRING_DELIMITER_REGEX = re.compile(
    RELATED_SUBJECT_STRING_DELIMITER_PATTERN
)
