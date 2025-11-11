from core.seeders.BaseSeeder import BaseSeeder
from app.modules.community.models import Community
from app.modules.auth.models import User
from app.modules.followCommunity.models import Followcommunity 


class FollowcommunitySeeder(BaseSeeder):

    priority = 4  # Ejecutarlo después de CommunitySeeder y AuthSeeder

    def run(self):
        # Obtener usuarios
        user = User.query.first()
        if not user:
            raise Exception("No hay usuarios disponibles para seguir comunidades. Ejecuta AuthSeeder primero.")
        
        # Obtener comunidades
        communities = Community.query.all()
        if not communities:
            raise Exception("No hay comunidades disponibles. Ejecuta CommunitySeeder primero.")

        data = []

        # Ejemplo simple: cada usuario sigue todas las comunidades
        for community in communities:
            data.append(
                Followcommunity(
                    community_id=community.id,
                    follower_id=user.id
                )
            )

        self.seed(data)
