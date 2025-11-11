from app.modules.followCommunity.repositories import FollowcommunityRepository
from core.services.BaseService import BaseService
from app import db
from modules.auth.models import User
from modules.community.models import Community

class FollowcommunityService(BaseService):
    def __init__(self):
        super().__init__(FollowcommunityRepository())

    def follow(user: User, community: Community):
        if user not in community.followers:
            community.followers.append(user)
            db.session.commit()

    def unfollow(user: User, community: Community):
        if user in community.followers:
            community.followers.remove(user)
            db.session.commit()