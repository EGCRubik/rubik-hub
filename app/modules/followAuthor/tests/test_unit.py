import pytest
from app import db
from app.modules.auth.models import User
from app.modules.dataset.models import DataSet, DSMetaData, Author, PublicationType
from app.modules.followAuthor.models import Followauthor
from app.modules.followAuthor.services import FollowauthorService
from app.modules.profile.models import UserProfile

follow_author_service = FollowauthorService()


@pytest.fixture(scope="module")
def test_client(test_client):
    with test_client.application.app_context():
        # Eliminar usuario si ya existe
        existing_user = User.query.filter_by(email="testfollow@example.com").first()
        if existing_user:
            db.session.delete(existing_user)
            db.session.commit()

        # Crear usuario y perfil
        user = User(email="testfollow@example.com", password="hashedpassword")
        db.session.add(user)
        db.session.commit()

        profile = UserProfile(
            user_id=user.id,
            name="Pepe",
            surname="Rubik",
            affiliation="Rubik Hub",
            orcid="0000-0001-2345-6789"
        )
        db.session.add(profile)
        db.session.commit()

        # Crear metadatos
        ds_meta = DSMetaData(
            title="Test Dataset",
            description="Descripción de prueba",
            publication_type=PublicationType.RECORDS
        )
        db.session.add(ds_meta)
        db.session.commit()

        # Crear autor válido
        author = Author(
            name="Pepe",
            affiliation="Rubik Hub",
            orcid="0000-0001-2345-6789",
            ds_meta_data_id=ds_meta.id
        )
        db.session.add(author)
        db.session.commit()

        # Crear dataset
        dataset = DataSet(user_id=user.id, ds_meta_data_id=ds_meta.id)
        db.session.add(dataset)
        db.session.commit()

        yield test_client


def test_follow_author_success(test_client):
    """Verifica que un usuario puede seguir a un autor correctamente."""
    with test_client.application.app_context(), test_client.application.test_request_context():
        user = User.query.filter_by(email="testfollow@example.com").first()
        author = Author.query.filter_by(orcid="0000-0001-2345-6789").first()

        follow = follow_author_service.follow(user, author)

        assert follow is not None, "No se creó la relación Followauthor"
        db_follow = Followauthor.query.filter_by(follower_id=user.id, author_id=author.id).first()
        assert db_follow is not None, "El registro no se guardó en la base de datos"


def test_follow_author_twice(test_client):
    """Verifica que no se pueda seguir dos veces al mismo autor."""
    with test_client.application.app_context(), test_client.application.test_request_context():
        user = User.query.filter_by(email="testfollow@example.com").first()
        author = Author.query.filter_by(orcid="0000-0001-2345-6789").first()

        follow_author_service.follow(user, author)
        follow_author_service.follow(user, author)

        follows = Followauthor.query.filter_by(follower_id=user.id, author_id=author.id).all()
        assert len(follows) == 1, "El usuario pudo seguir al mismo autor más de una vez"


def test_unfollow_author_success(test_client):
    """Verifica que un usuario pueda dejar de seguir correctamente a un autor."""
    with test_client.application.app_context(), test_client.application.test_request_context():
        user = User.query.filter_by(email="testfollow@example.com").first()
        author = Author.query.filter_by(orcid="0000-0001-2345-6789").first()

        # Asegurar que siga
        follow_author_service.follow(user, author)
        assert Followauthor.query.filter_by(follower_id=user.id, author_id=author.id).first() is not None

        # Ejecutar unfollow
        unfollowed = follow_author_service.unfollow(user, author)

        assert unfollowed is not None, "No devolvió el objeto al dejar de seguir"
        assert Followauthor.query.filter_by(follower_id=user.id, author_id=author.id).first() is None, \
            "El registro de follow no se eliminó"


def test_unfollow_without_follow(test_client):
    """Verifica que no falle si se intenta dejar de seguir a alguien que no se sigue."""
    with test_client.application.app_context(), test_client.application.test_request_context():
        user = User.query.filter_by(email="testfollow@example.com").first()
        author = Author.query.filter_by(orcid="0000-0001-2345-6789").first()

        # Eliminar si existe
        Followauthor.query.filter_by(follower_id=user.id, author_id=author.id).delete()
        db.session.commit()

        result = follow_author_service.unfollow(user, author)

        assert result is None, "Debe devolver None si no se seguía al autor"
        assert Followauthor.query.filter_by(follower_id=user.id, author_id=author.id).first() is None
