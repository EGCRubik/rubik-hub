from datetime import datetime
from enum import Enum

from app import db
from app.modules.dataset.models import DataSet


class Community(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(80), unique=True, nullable=False) # URL-friendly identifier
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    banner_color = db.Column(db.String(7), nullable=True)  # Hex color code
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Curators relationship
    curators = db.relationship(
        'User',
        secondary='community_curators',
        backref=db.backref('curated_communities', lazy='dynamic'),
        lazy='dynamic'
    )

    # Datasets relationship (with states)
    datasets_links = db.relationship(
        'CommunityDataset',
        back_populates='community',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )

    def approved_datasets(self):
        return [link.dataset for link in self.datasets_links.filter_by(
            status=CommunityDatasetStatus.APPROVED
        ).all()]

class CommunityCurator(db.Model):
    __tablename__ = 'community_curators'
    community_id = db.Column(db.Integer, db.ForeignKey('community.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    added_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class CommunityDatasetStatus(Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    REMOVED = 'removed'

class CommunityDataset(db.Model):
    _tablename__ = 'community_dataset'
    id = db.Column(db.Integer, primary_key=True)
    community_id = db.Column(db.Integer, db.ForeignKey('community.id'), nullable=False)
    dataset_id = db.Column(db.Integer, db.ForeignKey('data_set.id'), nullable=False)
    status = db.Column(db.Enum(CommunityDatasetStatus), nullable=False, default=CommunityDatasetStatus.PENDING)
    proposed_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    community = db.relationship('Community', back_populates='datasets_links')
    dataset = db.relationship( DataSet, backref=db.backref('community_links', cascade='all, delete-orphan'))
