from typing import Optional


class AbbreviationCollision(Exception):
    def __init__(self, subject_name: Optional[str] = None):
        message = "Collision during abbreviation resolution"

        if subject_name is not None:
            message += f" for subject `{subject_name}`"

        super().__init__(message)
