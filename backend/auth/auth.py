from fastapi_users.authentication import (
    CookieTransport,
    JWTStrategy,
    AuthenticationBackend,
)

from backend.config import (
    SECRET_AUTH as SECRET,
    LIFETIME_SECONDS,
)


cookie_transport = CookieTransport(cookie_name="chat_auth", cookie_max_age=LIFETIME_SECONDS)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=LIFETIME_SECONDS)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)
