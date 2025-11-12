from core.seeders.BaseSeeder import BaseSeeder
from app.modules.auth.models import User
from app.modules.dataset.models import Author
from app.modules.followAuthor.models import Followauthor


class FollowauthorSeeder(BaseSeeder):

    priority = 4  # Asegúrate de que se ejecute después de AuthorSeeder y AuthSeeder

    def run(self):
        # Obtener un usuario (por simplicidad, el primero)
        user = User.query.first()
        if not user:
            raise Exception("No hay usuarios disponibles para seguir autores. Ejecuta AuthSeeder primero.")

        # Obtener autores
        authors = Author.query.all()
        if not authors:
            raise Exception("No hay autores disponibles. Ejecuta AuthorSeeder primero.")

        data = []

        # Ejemplo simple: el usuario sigue a todos los autores
        for author in authors:
            if author.id % 2 == 0:  # Por ejemplo, sigue solo a autores con ID 
                data.append(
                    Followauthor(
                        author_id=author.id,
                        follower_id=user.id
                    )
                )

        self.seed(data)
