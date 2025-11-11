from app.modules.followAuthor.repositories import FollowauthorRepository
from core.services.BaseService import BaseService


class FollowauthorService(BaseService):
    def __init__(self):
        super().__init__(FollowauthorRepository())
