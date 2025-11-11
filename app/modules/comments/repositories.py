from app.modules.comments.models import Comments
from core.repositories.BaseRepository import BaseRepository


class CommentsRepository(BaseRepository):
    def __init__(self):
        super().__init__(Comments)
