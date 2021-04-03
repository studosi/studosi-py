from typing import Optional


def generate_install(use_sudo: bool = False):
    prefix = "sudo " if use_sudo else ""

    to_return = ""
    to_return += f"{prefix}apt install -y \\\n"
    to_return += "\tmariadb-server \\\n"
    to_return += "\tmariadb-client\n"

    return to_return


def generate_init(use_sudo: bool = False, use_mariadb: bool = True):
    prefix = "sudo " if use_sudo else ""
    service_name = "mariadb" if use_mariadb else "mysql"

    to_return = ""
    to_return += f"{prefix}systemctl enable {service_name}.service\n"
    to_return += f"{prefix}systemctl restart {service_name}.service\n"

    return to_return


def generate_setup(
    timeout: int = 10,
    root_password: Optional[str] = None,
    set_root_password: bool = True,
    new_root_password: Optional[str] = None,
    remove_anonymous_users: bool = True,
    disallow_root_login_remotely: bool = True,
    remove_test_database_and_access_to_it: bool = True,
    reload_privilege_tables_now: bool = True,
    use_sudo: bool = False,
    use_mariadb: bool = True,
):
    prefix = "sudo " if use_sudo else ""
    service_name = "mariadb" if use_mariadb else "mysql"

    to_return = ""
    to_return += f"{prefix}set timeout {timeout}\n"
    to_return += f"{prefix}spawn mysql_secure_installation\n\n"

    if root_password is None:
        root_password = ""

    to_return += 'expect "Enter current password for root (enter for none):"\n'
    to_return += f'send "{root_password}\\r"\n\n'

    to_return += 'expect "Set root password? [Y/n]"\n'
    to_return += 'send "' + ("y" if set_root_password else "n") + '\\r"\n'

    if set_root_password:
        to_return += 'expect "New password:"\n'
        to_return += f'send "{new_root_password}\\r"\n'

        to_return += 'expect "Re-enter new password:"\n'
        to_return += f'send "{new_root_password}\\r"\n'

    to_return += '\nexpect "Remove anonymous users? [Y/n]"\n'
    to_return += 'send "' + ("y" if remove_anonymous_users else "n") + '\\r"\n'

    to_return += 'expect "Disallow root login remotely? [Y/n]"\n'
    to_return += 'send "' + ("y" if disallow_root_login_remotely else "n") + '\\r"\n'

    to_return += 'expect "Remove test database and access to it? [Y/n]"\n'
    to_return += (
        'send "' + ("y" if remove_test_database_and_access_to_it else "n") + '\\r"\n'
    )

    to_return += '"Reload privilege tables now? [Y/n]"\n'
    to_return += 'send "' + ("y" if reload_privilege_tables_now else "n") + '\\r"\n\n'

    to_return += f"{prefix}systemctl restart {service_name}.service\n"

    return to_return
