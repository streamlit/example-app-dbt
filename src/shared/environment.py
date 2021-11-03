import os
from dataclasses import dataclass


@dataclass
class Auth:
    user: str
    password: str
    auth_success: bool = False

    def is_auth(self) -> bool:
        """Checks if the user has introduced the correct user and password

        Returns
        -------
        bool
            Wether the user introduced the correct user and pass or not
        """

        if (
            not self.auth_success
            and self.user == os.environ["DASHBOARD_USER"]
            and self.password == os.environ["DASHBOARD_PASS"]
        ):
            self.auth_success = True

        return self.auth_success
