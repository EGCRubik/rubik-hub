import pytest
from app import db
from app.modules.auth.models import User
from app.modules.community.models import Community
from app.modules.followCommunity.models import Followcommunity
from app.modules.followCommunity.services import FollowcommunityService
from app.modules.profile.models import UserProfile

follow_community_service = FollowcommunityService()


@pytest.fixture(scope="module")
def test_client(test_client):
    """Extiende el test_client para añadir datos específicos de followCommunity."""
    with test_client.application.app_context():
        # Eliminar usuario si ya existe
        existing_user = User.query.filter_by(email="testfollowcomm@example.com").first()
        if existing_user:
            db.session.delete(existing_user)
            db.session.commit()

        # Crear usuario y perfil
        user = User(email="testfollowcomm@example.com", password="hashedpassword")
        db.session.add(user)
        db.session.commit()

        profile = UserProfile(
            user_id=user.id,
            name="Ana",
            surname="Community",
            affiliation="Community Hub",
            orcid="0000-0001-9876-5432"
        )
        db.session.add(profile)
        db.session.commit()

        # Crear comunidad de prueba con usuario creador
        community = Community(
            name="Test Community",
            slug="test-community",
            description="Comunidad de prueba",
            created_by_id=user.id
        )
        db.session.add(community)
        db.session.commit()

        yield test_client

def test_follow_community_success(test_client):
    """Verifica que un usuario puede seguir a una comunidad correctamente."""
    with test_client.application.app_context(), test_client.application.test_request_context():
        user = User.query.filter_by(email="testfollowcomm@example.com").first()
        community = Community.query.filter_by(slug="test-community").first()

        follow = follow_community_service.follow(user, community)

        assert follow is not None, "No se creó la relación Followcommunity"
        db_follow = Followcommunity.query.filter_by(follower_id=user.id, community_id=community.id).first()
        assert db_follow is not None, "El registro no se guardó en la base de datos"


def test_follow_community_twice(test_client):
    """Verifica que no se pueda seguir dos veces a la misma comunidad."""
    with test_client.application.app_context(), test_client.application.test_request_context():
        user = User.query.filter_by(email="testfollowcomm@example.com").first()
        community = Community.query.filter_by(slug="test-community").first()

        follow_community_service.follow(user, community)
        follow_community_service.follow(user, community)

        follows = Followcommunity.query.filter_by(follower_id=user.id, community_id=community.id).all()
        assert len(follows) == 1, "El usuario pudo seguir a la misma comunidad más de una vez"


def test_unfollow_community_success(test_client):
    """Verifica que un usuario pueda dejar de seguir correctamente a una comunidad."""
    with test_client.application.app_context(), test_client.application.test_request_context():
        user = User.query.filter_by(email="testfollowcomm@example.com").first()
        community = Community.query.filter_by(slug="test-community").first()

        # Asegurar que siga
        follow_community_service.follow(user, community)
        assert Followcommunity.query.filter_by(follower_id=user.id, community_id=community.id).first() is not None

        # Ejecutar unfollow
        unfollowed = follow_community_service.unfollow(user, community)

        assert unfollowed is not None, "No devolvió el objeto al dejar de seguir"
        assert Followcommunity.query.filter_by(follower_id=user.id, community_id=community.id).first() is None, \
            "El registro de follow no se eliminó"


def test_unfollow_without_follow(test_client):
    """Verifica que no falle si se intenta dejar de seguir a una comunidad que no se sigue."""
    with test_client.application.app_context(), test_client.application.test_request_context():
        user = User.query.filter_by(email="testfollowcomm@example.com").first()
        community = Community.query.filter_by(slug="test-community").first()

        # Eliminar cualquier follow previo
        Followcommunity.query.filter_by(follower_id=user.id, community_id=community.id).delete()
        db.session.commit()

        result = follow_community_service.unfollow(user, community)

        assert result is None, "Debe devolver None si no se seguía a la comunidad"
        assert Followcommunity.query.filter_by(follower_id=user.id, community_id=community.id).first() is None
