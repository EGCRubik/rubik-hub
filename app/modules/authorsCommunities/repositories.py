from app.modules.authorsCommunities.models import Authorscommunities
from core.repositories.BaseRepository import BaseRepository


class AuthorscommunitiesRepository(BaseRepository):
    def __init__(self):
        super().__init__(Authorscommunities)
