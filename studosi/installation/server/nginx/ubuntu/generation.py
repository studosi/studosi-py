def generate_install(use_sudo: bool = False):
    prefix = "sudo " if use_sudo else ""

    return f"{prefix}apt install nginx\n"


def generate_init(use_sudo: bool = False):
    prefix = "sudo " if use_sudo else ""

    to_return = ""
    to_return += f"{prefix}systemctl enable nginx.service\n"
    to_return += f"{prefix}systemctl restart nginx.service\n"

    return to_return
