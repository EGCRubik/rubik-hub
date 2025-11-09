from app.modules.followCommunity.models import Followcommunity
from core.repositories.BaseRepository import BaseRepository


class FollowcommunityRepository(BaseRepository):
    def __init__(self):
        super().__init__(Followcommunity)
