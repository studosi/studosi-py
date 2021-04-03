REGEX_SUFFIX = r"\s*=[^\r\n]*"
PHP_ORIGIN = (
    f"file_uploads{REGEX_SUFFIX}",
    f"allow_url_fopen{REGEX_SUFFIX}",
    f"memory_limit{REGEX_SUFFIX}",
    f"upload_max_filesize{REGEX_SUFFIX}",
    f"cgi.fix_pathinfo{REGEX_SUFFIX}",
    f"max_execution_time{REGEX_SUFFIX}",
    f"date.timezone{REGEX_SUFFIX}",
)
