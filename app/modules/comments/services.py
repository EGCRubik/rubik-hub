from app.modules.comments.repositories import CommentsRepository
from core.services.BaseService import BaseService


class CommentsService(BaseService):
    def __init__(self):
        super().__init__(CommentsRepository())
