from app import db


class TwoFactor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    key = db.Column(db.String(255), nullable=False)
    qrcode = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'TwoFactor<{self.id}>'
