from fastapi import APIRouter
from app.routers.admin.auth import router as auth_router
from app.routers.admin.place_admin_router import router as place_router
from app.routers.admin.category_admin_router import router as category_router
from app.routers.admin.upload import router as upload_router
from app.routers.admin.user_management import router as admin_user_router
router = APIRouter(prefix="/api")
router.include_router(auth_router,prefix="/admin")
router.include_router(place_router,prefix="/admin")
router.include_router(category_router,prefix="/admin")
router.include_router(upload_router, prefix="/admin")
router.include_router(admin_user_router, prefix="/admin")