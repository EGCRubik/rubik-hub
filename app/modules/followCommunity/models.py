from app import db
from app.modules.community.models import Community
from app.modules.auth.models import User

class Followcommunity(db.Model):
    __tablename__ = "followcommunity"

    id = db.Column(db.Integer, primary_key=True)

    community_id = db.Column(db.Integer, db.ForeignKey("community.id"), nullable=False)
    community = db.relationship("Community", backref=db.backref("followers", lazy="dynamic"))

    follower_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    follower = db.relationship("User", backref=db.backref("followed_communities", lazy="dynamic"))

    def __repr__(self):
        return f'Followcommunity<{self.id}>'
