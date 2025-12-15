import pytest
import pyotp

from app import db
from app.modules.auth.models import User
from app.modules.two_factor.models import TwoFactor
from app.modules.two_factor.services import TwoFactorService
from app.modules.two_factor.repositories import TwoFactorRepository
from app.modules.conftest import login, logout
from app.modules.profile.models import UserProfile


@pytest.fixture(scope='module')
def test_client(test_client):
    with test_client.application.app_context():
        existing = User.query.filter_by(email='user1@example.com').first()
        if existing:
            db.session.delete(existing)
            db.session.commit()

        user = User(email='user1@example.com', password='1234')
        db.session.add(user)
        db.session.commit()

        yield test_client

def test_create_two_factor_entry(clean_database, test_client):
    """
    Test creating a two-factor authentication entry for a user.
    """
    with test_client.application.app_context(), test_client.application.test_request_context():
        user = User.query.filter_by(email='user1@example.com').first()
        if user is None:
            user = User(email='user1@example.com', password='1234')
            db.session.add(user)
            db.session.commit()

        # Create 2FA entry
        service = TwoFactorService()
        key = pyotp.random_base32()
        uri = pyotp.totp.TOTP(key).provisioning_uri(name=user.email, issuer_name="RubikHub")
        
        two_factor = service.create_two_factor_entry(user.id, key, uri)

        assert two_factor is not None
        assert two_factor.user_id == user.id
        assert two_factor.key == key
        assert two_factor.uri == uri


def test_get_by_user_id(clean_database, test_client):
    """
    Test retrieving a two-factor entry by user ID.
    """
    with test_client.application.app_context(), test_client.application.test_request_context():
        user = User.query.filter_by(email='user1@example.com').first()
        if user is None:
            user = User(email='user1@example.com', password='1234')
            db.session.add(user)
            db.session.commit()

        key = pyotp.random_base32()
        uri = pyotp.totp.TOTP(key).provisioning_uri(name=user.email, issuer_name="RubikHub")
        
        two_factor = TwoFactor(user_id=user.id, key=key, uri=uri)
        db.session.add(two_factor)
        db.session.commit()

        # Retrieve via service
        service = TwoFactorService()
        retrieved = service.get_by_user_id(user.id)

        assert retrieved is not None
        assert retrieved.user_id == user.id
        assert retrieved.key == key


def test_delete_by_user_id(clean_database, test_client):
    """
    Test deleting a two-factor entry by user ID.
    """
    with test_client.application.app_context(), test_client.application.test_request_context():
        user = User.query.filter_by(email='user1@example.com').first()
        if user is None:
            user = User(email='user1@example.com', password='1234')
            db.session.add(user)
            db.session.commit()

        key = pyotp.random_base32()
        uri = pyotp.totp.TOTP(key).provisioning_uri(name=user.email, issuer_name="RubikHub")
        
        two_factor = TwoFactor(user_id=user.id, key=key, uri=uri)
        db.session.add(two_factor)
        db.session.commit()

        # Delete via service
        service = TwoFactorService()
        service.delete_by_user_id(user.id)

        # Verify deletion
        retrieved = service.get_by_user_id(user.id)
        assert retrieved is None


# def test_enable_two_factor_via_post(test_client):
#     """
#     Test enabling two-factor authentication via POST request to update endpoint.
#     """
#     # Login as test user
#     login_response = login(test_client, "twofactor@example.com", "test1234")
#     assert login_response.status_code == 200, "Login was unsuccessful."

#     # Enable 2FA via POST
#     response = test_client.post(
#         "/two_factor/update-factor-enabled",
#         data={"enabled": "1"},
#         follow_redirects=False
#     )

#     assert response.status_code == 302, "Should redirect to setup page"
    
#     # Verify redirect URL contains twofactor-setup
#     assert "/profile/twofactor-setup" in response.location or "twofactor" in response.location

#     logout(test_client)


# def test_disable_two_factor_via_post(test_client):
#     """
#     Test disabling two-factor authentication via POST request.
#     """
#     with test_client.application.app_context():
#         # Setup: Create user with 2FA enabled
#         user = User.query.filter_by(email="twofactor@example.com").first()
#         user.factor_enabled = True
        
#         key = pyotp.random_base32()
#         uri = pyotp.totp.TOTP(key).provisioning_uri(name=user.email, issuer_name="RubikHub")
#         two_factor = TwoFactor(user_id=user.id, key=key, uri=uri)
#         db.session.add(two_factor)
#         db.session.commit()

#     # Login
#     login_response = login(test_client, "twofactor@example.com", "test1234")
#     assert login_response.status_code == 200

#     # Disable 2FA
#     response = test_client.post(
#         "/two_factor/update-factor-enabled",
#         data={"enabled": "0"},
#         follow_redirects=True
#     )

#     assert response.status_code == 200
#     assert b'"factor_enabled": false' in response.data or b'"factor_enabled":false' in response.data

#     logout(test_client)

