from core.seeders.BaseSeeder import BaseSeeder
from app.modules.community.models import Community
from app.modules.community.models import CommunityCurator
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
                slug="cubos-2x2",
                name="Cubos 2x2",
                description="Una comunidad dedicada al aprendizaje y discusión sobre Cubos de Rubik 2x2.",
                banner_color="#2D9CDB",
                created_by_id=user.id
            ),
            Community(
                slug="cubos-in-the-house",
                name="Cubos in the House",
                description="Comunidad dedicada a los entusiastas de los cubos de Rubik.",
                banner_color="#27AE60",
                created_by_id=user.id
            ),
            Community(
                slug="rubik-is-my-dad",
                name="Rubik is my Dad",
                description="Para aquellos que consideran al cubo de Rubik como una parte esencial de sus vidas.",
                banner_color="#6FCF97",
                created_by_id=user.id
            )
        ]

        self.seed(data)

        curators_data = [
            CommunityCurator(
                community_id=1,
                user_id=1
            ),
            CommunityCurator(
                community_id=2,
                user_id=2
            ),
            CommunityCurator(
                community_id=3,
                user_id=1
            ),
            CommunityCurator(
                community_id=3,
                user_id=2
            )
        ]   
        
        self.seed(curators_data)
