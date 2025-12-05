from app import db


class TwoFactor(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return f'TwoFactor<{self.id}>'
