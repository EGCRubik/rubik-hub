from app.modules.two_factor.repositories import TwoFactorRepository
from core.services.BaseService import BaseService


class TwoFactorService(BaseService):
    def __init__(self):
        super().__init__(TwoFactorRepository())
