import os
from datetime import datetime

from flask import current_app
from werkzeug.utils import secure_filename

from app import db
from app.modules.community.repositories import CommunityRepository
from core.services.BaseService import BaseService

from .models import Community, CommunityCurator, CommunityDataset, CommunityDatasetStatus


class CommunityService:
    def create(self, form, creator):
        community = Community(
            name=form.name.data,
            slug=form.slug.data,
            description=form.description.data,
            banner_color=form.banner_color.data,
            created_by_id=creator.id
        )
        db.session.add(community)
        db.session.flush() # To get the community ID

        db.session.add(CommunityCurator(
            community_id=community.id,
            user_id=creator.id
        ))

        db.session.commit()
        return community
    
    def list_all(self):
        return Community.query.order_by(Community.created_at.desc()).all()
    
    def is_curator(self, community, user):
        return community.curators.filter(CommunityCurator.user_id == user.id).count() > 0
    
    def get_by_slug(self, slug):
        return Community.query.filter_by(slug=slug).first_or_404()
    
class CommunityDatasetService:
    def propose(self, community, dataset, proposer):
        link = CommunityDataset(
            community_id=community.id,
            dataset_id=dataset.id,
            status=CommunityDatasetStatus.PENDING,
            proposed_by_id=proposer.id
        )
        db.session.add(link)
        db.session.commit()
        return link
    
    def set_status(self, link_id, status, current_user=None):
        link = CommunityDataset.query.get_or_404(link_id)
        if link:
            link.status = status
            db.session.commit()
        return link
