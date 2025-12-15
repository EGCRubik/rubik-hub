import pytest

from app import db
from app.modules.auth.models import User
from app.modules.comments.models import Comments
from app.modules.comments.services import CommentsService
from app.modules.dataset.models import Author, DataSet, DSMetaData, PublicationType
from app.modules.profile.models import UserProfile

comments_service = CommentsService()

@pytest.fixture(scope="module")
def test_client(test_client):
    with test_client.application.app_context():
        # Eliminar usuario si ya existe
        existing_user = User.query.filter_by(email="testcomments@example.com").first()
        if existing_user:
            db.session.delete(existing_user)
            db.session.commit()

        # Crear usuario y perfil
        user = User(email="testcomments@example.com", password="hashedpassword")
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


        # Crear metadatos
        ds_meta = DSMetaData(
            title="Test Dataset",
            description="Descripción de prueba",
            publication_type=PublicationType.SALES
        )
        db.session.add(ds_meta)
        db.session.commit()

        # Crear autor válido y asociarlo al DSMetaData
        author = Author(
            name="Pepe",
            affiliation="Rubik Hub",
            orcid="0000-0001-2345-6789",
        )
        db.session.add(author)
        db.session.commit()

        ds_meta.author_id = author.id
        db.session.add(ds_meta)
        db.session.commit()

        # Crear dataset
        dataset = DataSet(user_id=user.id, ds_meta_data_id=ds_meta.id)
        db.session.add(dataset)
        db.session.commit()

        yield test_client


def test_create_comment(test_client):
    with test_client.application.app_context():
        with test_client.application.test_request_context():
            user = User.query.filter_by(email="testcomments@example.com").first()
            dataset = DataSet.query.first()
            author_id = user.profile.id
            content = "Este es un comentario de prueba"

            comment, returned_dataset = comments_service.create_comment(
                dataset_id=dataset.id,
                author_id=author_id,
                content=content
            )

            assert comment is not None, "El comentario no se creó correctamente"
            assert returned_dataset.id == dataset.id, "El dataset devuelto no coincide"
            assert comment.content == content, "El contenido del comentario no coincide"
            
def test_delete_comment(test_client):
    with test_client.application.app_context(), test_client.application.test_request_context():
        user = User.query.filter_by(email="testcomments@example.com").first()
        dataset = DataSet.query.first()

        # Crear comentario
        comment, _ = comments_service.create_comment(
            dataset_id=dataset.id,
            author_id=user.profile.id,
            content="Comentario para eliminar"
        )

        # Confirmar que existe
        assert comment is not None
        comment_id = comment.id
        assert Comments.query.get(comment_id) is not None

        # Eliminar comentario
        deleted, returned_dataset = comments_service.delete_comment(
            comment_id=comment_id,
            current_user=user
        )

        # Verificar eliminación
        assert deleted is not None, "El comentario no se eliminó"
        assert Comments.query.get(comment_id) is None, "El comentario sigue existiendo"
        assert returned_dataset.id == dataset.id
    
# He utilizado parcialmente la inteligencia artificial (IA) como herramienta de apoyo durante el desarrollo y modificación de este archivo de código. 
# La IA me ha ayudado a entender, optimizar y automatizar ciertas tareas, pero la implementación final y las decisiones clave han sido realizadas por mí.
