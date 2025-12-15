from app.modules.followCommunity.repositories import FollowcommunityRepository
from core.services.BaseService import BaseService
from app import db
from app.modules.auth.models import User
from app.modules.community.models import Community
from app.modules.followCommunity.models import Followcommunity

class FollowcommunityService(BaseService):
    def __init__(self):
        super().__init__(FollowcommunityRepository())

    def follow(self, user: User, community: Community):
        """Permite que un usuario siga a una comunidad si aún no la sigue."""
        # Verificar si ya existe
        existing = Followcommunity.query.filter_by(
            follower_id=user.id,
            community_id=community.id
        ).first()

        if not existing:
            follow = Followcommunity(
                follower_id=user.id,
                community_id=community.id
            )
            db.session.add(follow)
            db.session.commit()
            return follow
        # Si ya sigue, devolver None
        return None

    def unfollow(self, user: User, community: Community):
        """Permite que un usuario deje de seguir una comunidad si la sigue."""
        existing = Followcommunity.query.filter_by(
            follower_id=user.id,
            community_id=community.id
        ).first()

        if existing:
            db.session.delete(existing)
            db.session.commit()
            return existing

        # Si no estaba siguiendo, devolver None
        return None
