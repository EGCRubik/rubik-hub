from app.modules.followAuthor.repositories import FollowauthorRepository
from core.services.BaseService import BaseService
from app import db
from modules.auth.models import User
from modules.dataset.models import Author

class FollowauthorService(BaseService):
    def __init__(self):
        super().__init__(FollowauthorRepository())

    def follow(user: User, author: Author):
        if user not in author.followers:
            author.followers.append(user)
            db.session.commit()

    def unfollow(user: User, author: Author):
        if user in author.followers:
            author.followers.remove(user)
            db.session.commit()