from app import db
from app.modules.followAuthor.models import Followauthor


class FollowauthorService:
    def follow(self, user, author):
        """Crea una relación de seguimiento entre un usuario y un autor."""
        existing = Followauthor.query.filter_by(
            follower_id=user.id, author_id=author.id
        ).first()

        if not existing:
            follow = Followauthor(follower_id=user.id, author_id=author.id)
            db.session.add(follow)
            db.session.commit()
            return follow
        return existing

    def unfollow(self, user, author):
        """Elimina la relación de seguimiento si existe."""
        existing = Followauthor.query.filter_by(
            follower_id=user.id, author_id=author.id
        ).first()

        if existing:
            db.session.delete(existing)
            db.session.commit()
            return existing
        return None
