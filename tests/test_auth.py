import pytest
import bcrypt

from mcps.auth.provider import McpsOAuthProvider


def _hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


@pytest.mark.unit
class TestMcpsOAuthProvider:
    def test_verify_credentials_valid(self):
        users = {"alice": _hash("secret123")}
        provider = McpsOAuthProvider(
            base_url="http://localhost:8000",
            users=users,
        )
        assert provider.verify_credentials("alice", "secret123") is True

    def test_verify_credentials_invalid_password(self):
        users = {"alice": _hash("secret123")}
        provider = McpsOAuthProvider(
            base_url="http://localhost:8000",
            users=users,
        )
        assert provider.verify_credentials("alice", "wrongpass") is False

    def test_verify_credentials_unknown_user(self):
        users = {"alice": _hash("secret123")}
        provider = McpsOAuthProvider(
            base_url="http://localhost:8000",
            users=users,
        )
        assert provider.verify_credentials("bob", "secret123") is False

    def test_empty_users(self):
        provider = McpsOAuthProvider(
            base_url="http://localhost:8000",
            users={},
        )
        assert provider.verify_credentials("anyone", "anything") is False
