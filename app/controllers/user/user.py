from fastapi import HTTPException
from passlib.context import CryptContext

from app.models.user import UserRegister, UserInDB, UserResponse

# cấu hình bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash password bằng bcrypt
    bcrypt chỉ hỗ trợ tối đa 72 ký tự
    """
    safe_password = password[:72]
    return pwd_context.hash(safe_password)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Dùng cho login sau này
    """
    return pwd_context.verify(password[:72], hashed_password)


async def register_user_controller(
    user: UserRegister,
    users_col
) -> UserResponse:

    # kiểm tra email đã tồn tại
    existing_user = await users_col.find_one({"email": user.email})

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # tạo user mới
    user_db = UserInDB(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password)
    )

    result = await users_col.insert_one(user_db.model_dump())

    # trả response cho client
    return UserResponse(
        id=str(result.inserted_id),
        username=user.username,
        email=user.email
    )