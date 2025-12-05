from app.modules.two_factor.models import TwoFactor
from core.repositories.BaseRepository import BaseRepository


class TwoFactorRepository(BaseRepository):
    def __init__(self):
        super().__init__(TwoFactor)

    def get_by_user_id(self, user_id: int) -> TwoFactor | None:
        return self.session.query(self.model).filter_by(user_id=user_id).first()
