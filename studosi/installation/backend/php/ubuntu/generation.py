from studosi.constants.installation.backend.php.ubuntu import PHP_ORIGIN


def generate_prep(use_sudo: bool = False):
    prefix = "sudo " if use_sudo else ""

    to_return = ""
    to_return += f"{prefix}apt install -y software-properties-common\n"
    to_return += f"{prefix}add-apt-repository -y ppa:ondrej/php\n"
    to_return += f"{prefix}apt update -y\n"

    return to_return


def generate_install(version: str = "8.0", use_sudo: bool = False):
    prefix = "sudo " if use_sudo else ""
    php_prefix = f"php{version.strip()}"

    to_return = ""
    to_return += f"{prefix} apt install -y \\\n"
    to_return += f"\t{php_prefix}-fpm \\\n"
    to_return += f"\t{php_prefix}-common \\\n"
    to_return += f"\t{php_prefix}-mbstring \\\n"
    to_return += f"\t{php_prefix}-xmlrpc \\\n"
    to_return += f"\t{php_prefix}-soap \\\n"
    to_return += f"\t{php_prefix}-mysql \\\n"
    to_return += f"\t{php_prefix}-gd \\\n"
    to_return += f"\t{php_prefix}-xml \\\n"
    to_return += f"\t{php_prefix}-cli \\\n"
    to_return += f"\t{php_prefix}-zip\n"

    return to_return


def generate_setup(
    version: str = "8.0",
    file_uploads: bool = True,
    allow_url_fopen: bool = True,
    memory_limit: str = "256M",
    upload_max_filesize: str = "100M",
    cgi_fix_pathinfo: bool = False,
    max_execution_time: int = 360,
    date_timezone: str = "Europe/Zagreb",
    use_sudo: bool = True,
):
    prefix = "sudo " if use_sudo else ""

    path = f"/etc/php/{version}/fpm/php.ini"

    replacement = (
        "file_uploads = " + ("On" if file_uploads else "Off"),
        "allow_url_fopen = " + ("On" if allow_url_fopen else "Off"),
        f"memory_limit = {memory_limit.strip()}",
        f"upload_max_filesize = {upload_max_filesize.strip()}",
        "cgi.fix_pathinfo = " + ("0" if cgi_fix_pathinfo else "1"),
        f"max_execution_time = {max_execution_time}",
        f"date.timezone = {date_timezone.strip()}",
    )

    to_return = ""

    for src, dest in zip(PHP_ORIGIN, replacement):
        to_return += f'{prefix}sed -i "s/{src}/{dest}/g {path}\n'

    to_return += f"\n{prefix}systemctl restart nginx.service\n"

    return to_return
