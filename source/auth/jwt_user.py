from starlette.authentication import BaseUser


class JWTUser(BaseUser):
    def __init__(self, user_id: int, username: str, token: str, **kw) -> None:
        self.user_id = user_id
        self.username = username
        self.token = token

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.username

    @property
    def identity(self) -> str:
        return "some string"
