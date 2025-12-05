from locust import User
from app.modules.two_factor.repositories import TwoFactorRepository
from core.services.BaseService import BaseService
from app.modules.auth.services import AuthenticationService

authentication_service = AuthenticationService()

class TwoFactorService(BaseService):
    def __init__(self):
        super().__init__(TwoFactorRepository())

    def create_two_factor_entry(self, user_id: int, key: str, uri: str):
        data = {
            "user_id": user_id,
            "key": key,
            "uri": uri,
        }
        return self.create(**data)
    
    def get_by_user_id(self, user_id: int):
        return self.repository.get_by_user_id(user_id)
    
    def delete_by_user_id(self, user_id: int):
        two_factor_entry = self.get_by_user_id(user_id)
        if two_factor_entry:
            self.repository.delete(two_factor_entry.id)

    def update_factor_enabled(self, factor_enabled: bool) -> User:
        user = authentication_service.get_authenticated_user()
        if user is None:
            raise ValueError("User not found.")
        
        user.factor_enabled = factor_enabled
        self.repository.session.commit()
        return user
