"""
Tests unitarios para el módulo de seguridad: hashing y JWT.
"""
import pytest
from datetime import timedelta

from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
)


class TestPasswordHashing:
    """Tests para hashing de contraseñas con bcrypt."""

    def test_hash_password(self):
        """get_password_hash genera un hash diferente al texto plano."""
        password = "mysecretpassword"
        hashed = get_password_hash(password)
        assert hashed != password
        assert len(hashed) > 0

    def test_verify_correct_password(self):
        """verify_password retorna True con contraseña correcta."""
        password = "mysecretpassword"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_verify_wrong_password(self):
        """verify_password retorna False con contraseña incorrecta."""
        hashed = get_password_hash("correctpassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_different_hashes_for_same_password(self):
        """Bcrypt genera hashes diferentes para la misma contraseña (salt)."""
        password = "samepassword"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        assert hash1 != hash2
        # Pero ambos verifican correctamente
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

    def test_hash_starts_with_bcrypt_prefix(self):
        """El hash generado usa el formato bcrypt ($2b$)."""
        hashed = get_password_hash("test")
        assert hashed.startswith("$2b$")


class TestJWT:
    """Tests para generación y decodificación de tokens JWT."""

    def test_create_and_decode_token(self):
        """Token creado se puede decodificar correctamente."""
        data = {"sub": "test-user-id"}
        token = create_access_token(data)
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "test-user-id"

    def test_token_has_expiration(self):
        """Token contiene campo de expiración."""
        token = create_access_token({"sub": "user1"})
        payload = decode_access_token(token)
        assert "exp" in payload

    def test_custom_expiration(self):
        """Token con expiración personalizada funciona."""
        token = create_access_token(
            {"sub": "user1"}, expires_delta=timedelta(hours=2)
        )
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "user1"

    def test_decode_invalid_token(self):
        """Token inválido retorna None."""
        result = decode_access_token("invalid.token.here")
        assert result is None

    def test_decode_empty_token(self):
        """Token vacío retorna None."""
        result = decode_access_token("")
        assert result is None

    def test_token_preserves_data(self):
        """Token preserva los datos adicionales del payload."""
        data = {"sub": "user-123", "role": "admin", "extra": "value"}
        token = create_access_token(data)
        payload = decode_access_token(token)
        assert payload["sub"] == "user-123"
        assert payload["role"] == "admin"
        assert payload["extra"] == "value"
