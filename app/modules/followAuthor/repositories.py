from app.modules.followAuthor.models import Followauthor
from core.repositories.BaseRepository import BaseRepository


class FollowauthorRepository(BaseRepository):
    def __init__(self):
        super().__init__(Followauthor)
