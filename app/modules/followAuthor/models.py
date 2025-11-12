from app import db


class Followauthor(db.Model):
    __tablename__ = "followauthor"

    id = db.Column(db.Integer, primary_key=True)

    author_id = db.Column(db.Integer, db.ForeignKey("author.id"), nullable=False)
    author = db.relationship("Author", backref=db.backref("followers", lazy="dynamic"))

    follower_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    follower = db.relationship("User", backref=db.backref("followed_authors", lazy="dynamic"))

    def __repr__(self):
        return f'Followauthor<{self.id}>'
