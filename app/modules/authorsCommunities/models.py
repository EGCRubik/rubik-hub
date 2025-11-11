from app import db


class Authorscommunities(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return f'Authorscommunities<{self.id}>'
