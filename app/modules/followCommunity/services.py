from app.modules.followCommunity.repositories import FollowcommunityRepository
from core.services.BaseService import BaseService


class FollowcommunityService(BaseService):
    def __init__(self):
        super().__init__(FollowcommunityRepository())
