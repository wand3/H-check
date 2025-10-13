from app.routes.main import main as h_check_router
from app.routes.auth import auth as auth_router
from app.routes.user import router as user_router

__all__ = [
    "h_check_router",
    "user_router",
    "auth_router"
]
