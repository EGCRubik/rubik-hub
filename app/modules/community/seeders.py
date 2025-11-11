from core.seeders.BaseSeeder import BaseSeeder
from app.modules.community.models import Community
from app.modules.auth.models import User  # Ajusta ruta según tu organización


class CommunitySeeder(BaseSeeder):

    priority = 3  # Se ejecuta después de DataSetSeeder

    def run(self):

        # Obtener un usuario creador (por ejemplo, el primero)
        user = User.query.first()

        if not user:
            raise Exception("Necesitas un Usuario creado antes de ejecutar este seeder.")

        data = [
            Community(
                slug="ciencia-de-datos",
                name="Ciencia de Datos",
                description="Una comunidad dedicada al aprendizaje y discusión sobre Ciencia de Datos.",
                banner_color="#2D9CDB",
                created_by_id=user.id
            ),
            Community(
                slug="economia",
                name="Economía",
                description="Recursos, datasets y análisis económicos.",
                banner_color="#27AE60",
                created_by_id=user.id
            ),
            Community(
                slug="medio-ambiente",
                name="Medio Ambiente",
                description="Comunidad enfocada en datos y análisis sobre sostenibilidad y medio ambiente.",
                banner_color="#6FCF97",
                created_by_id=user.id
            )
        ]

        self.seed(data)
