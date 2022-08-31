from pydantic import BaseModel

from class_based_fastapi import Routable, get


class User(BaseModel):
    username: str


class RepositoruUser:
    def find_user(self, username: str) -> User:
        return User(username=username)


class UserRoutes(Routable):
    # NAME_MODULE = 'NAME'
    """Inherits from Routable."""

    # Note injection here by simply passing values to the constructor. Other injection frameworks also
    # supported as there's nothing sepecial about this __init__ method.
    def __init__(self) -> None:
        """Constructor. The Dao is injected here."""
        super().__init__()
        self.repos = RepositoruUser()  # "Depend"

    @get('/user/{username}')
    def get_user_by_name(self, username: str) -> User:
        # Use our injected DAO instance.
        return self.repos.find_user(username)


class ParentUserRoutes(UserRoutes):
    NAME_MODULE = 'Test'
    # VERSION_API = '123'

    @get('')
    def get_user_by_name(self) -> User:
        # Use our injected DAO instance.
        return self.repos.find_user('test')
