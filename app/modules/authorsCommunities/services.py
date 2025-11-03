from app.modules.authorsCommunities.repositories import AuthorscommunitiesRepository
from core.services.BaseService import BaseService


class AuthorscommunitiesService(BaseService):
    def __init__(self):
        super().__init__(AuthorscommunitiesRepository())
