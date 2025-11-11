from app import db


class Followauthor(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return f'Followauthor<{self.id}>'
