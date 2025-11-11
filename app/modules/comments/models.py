from app import db
from datetime import datetime
from app.modules.dataset.models import Author
from app.modules.dataset.models import DataSet

class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Relación con Author
    author_id = db.Column(db.Integer, db.ForeignKey("author.id"), nullable=False)
    author = db.relationship("Author")

    # Nueva relación con DataSet
    dataset_id = db.Column(db.Integer, db.ForeignKey("data_set.id"), nullable=False)
    dataset = db.relationship(DataSet, backref="comments")

    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'Comments<{self.author.name} on DataSet {self.dataset_id}>'
