import json

import pytest

from app import db
from app.modules.auth.models import User
from app.modules.community.models import Community, CommunityCurator, CommunityDataset, CommunityDatasetStatus
from app.modules.community.services import CommunityDatasetService, CommunityService
from app.modules.dataset.models import DataSet, DSMetaData, PublicationType
from app.modules.profile.models import UserProfile

community_service = CommunityService()
link_service = CommunityDatasetService()


@pytest.fixture(scope='module')
def test_client(test_client):
    with test_client.application.app_context():
        # Ensure test user does not already exist
        existing = User.query.filter_by(email='user1@example.com').first()
        if existing:
            db.session.delete(existing)
            db.session.commit()

        # Create a user for the tests
        user = User(email='user1@example.com', password='1234')
        db.session.add(user)
        db.session.commit()

        yield test_client


def test_create_community_service(test_client):
    """Verifica que CommunityService.create persiste la comunidad y añade al creador como curador."""
    with test_client.application.app_context(), test_client.application.test_request_context():
        user = User.query.filter_by(email='user1@example.com').first()
        # If clean_database fixture ran it may have removed the module user; recreate it here
        if user is None:
            user = User(email='user1@example.com', password='1234')
            db.session.add(user)
            db.session.commit()
        
        # Build a minimal form-like object expected by the service
        class F:
            pass

        f = F()
        f.name = type('X', (), {'data': 'Comunidad Test'})
        f.slug = type('X', (), {'data': 'comunidad-test'})
        f.description = type('X', (), {'data': 'Descripción'})
        f.banner_color = type('X', (), {'data': '#123456'})

        community = community_service.create(f, user)
        assert community.id is not None
        assert community.name == 'Comunidad Test'
        # is_curator should return True for the creator
        assert community_service.is_curator(community, user)


def test_propose_and_set_status(clean_database, test_client):
    """Verifica que se puede proponer un dataset a una comunidad y cambiar su estado."""
    with test_client.application.app_context(), test_client.application.test_request_context():

        existing_user = User.query.filter_by(email="testcomments@example.com").first()
        if existing_user:
            db.session.delete(existing_user)
            db.session.commit()
        
        user = User(email="testcommunity@example.com", password="hashedpassword")
        db.session.add(user)
        db.session.commit()

        profile = UserProfile(
        user_id=user.id,
        name="Pepe",
        surname="Rubik",
        affiliation="Rubik Hub",
        orcid="0000-0001-2345-6789")
        db.session.add(profile)
        db.session.commit()

        # Create a community directly
        community = Community(name='Prop Community', slug='prop-community', description='x', created_by_id=user.id)
        db.session.add(community)
        db.session.flush()
        # Add creator as curator
        db.session.add(CommunityCurator(community_id=community.id, user_id=user.id))
        db.session.commit()

        # Create DSMetaData and dataset
        meta = DSMetaData(title='DS Test', description='desc', publication_type=PublicationType.NONE)
        db.session.add(meta)
        db.session.flush()
        ds = DataSet(user_id=user.id, ds_meta_data_id=meta.id)
        db.session.add(ds)
        db.session.commit()

        # Propose
        link = link_service.propose(community, ds, user)
        assert link.id is not None
        assert link.status == CommunityDatasetStatus.PENDING

        # Approve
        approved = link_service.set_status(link.id, CommunityDatasetStatus.APPROVED, user)
        assert approved.status == CommunityDatasetStatus.APPROVED

        # Create another link and reject
        link2 = link_service.propose(community, ds, user)
        rejected = link_service.set_status(link2.id, CommunityDatasetStatus.REJECTED, user)
        assert rejected.status == CommunityDatasetStatus.REJECTED


