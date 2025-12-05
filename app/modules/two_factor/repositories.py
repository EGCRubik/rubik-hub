from app.modules.two_factor.models import TwoFactor
from core.repositories.BaseRepository import BaseRepository


class TwoFactorRepository(BaseRepository):
    def __init__(self):
        super().__init__(TwoFactor)
