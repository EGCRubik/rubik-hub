from app import db
from app.modules.community.models import Community

class Followcommunity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    community_id = db.Column(db.Integer, db.ForeignKey("community.id"), nullable=False)
    community = db.relationship(Community, backref="followers")

    
    follower_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    follower = db.relationship("User", backref="followed_communities")

    def __repr__(self):
        return f'Followcommunity<{self.id}>'
