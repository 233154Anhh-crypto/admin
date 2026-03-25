from bson import ObjectId
from datetime import datetime


def serialize(user):
    if not user:
        return None

    return {
        "id": str(user["_id"]),
        "username": user.get("username"),
        "email": user.get("email"),
        "role": user.get("role", "user"),  # 👈 thêm role
        "created_at": user.get("created_at")
    }


# GET ALL USERS (chỉ admin nên dùng cái này)
async def get_users(collection):
    cursor = collection.find()
    result = []

    async for user in cursor:
        result.append(serialize(user))

    return result


# CREATE USER
async def create_user(data, collection):
    # loại bỏ trường không hỗ trợ từ data
    user_data = {k: v for k, v in data.dict().items() if v is not None}

    # kiểm tra tồn tại email hoặc username
    if await collection.find_one({"email": user_data.get("email")}):
        return {"error": "Email already registered"}

    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

    if "password" not in user_data or not user_data.get("password"):
        user_data["password"] = "123456"

    user_data["hashed_password"] = pwd_context.hash(user_data.pop("password"))
    user_data.setdefault("role", "user")
    user_data["created_at"] = datetime.utcnow()

    result = await collection.insert_one(user_data)

    return serialize({**user_data, "_id": result.inserted_id})


# GET ONE USER
async def get_user(user_id: str, collection):
    try:
        user = await collection.find_one({"_id": ObjectId(user_id)})
    except:
        return {"error": "Invalid user id"}

    if not user:
        return {"error": "User not found"}

    return serialize(user)


# UPDATE USER
async def update_user(user_id: str, data, collection):
    try:
        obj_id = ObjectId(user_id)
    except:
        return {"error": "Invalid user id"}

    update_data = data.dict(exclude_none=True)

    # ❌ không cho sửa mấy field quan trọng
    update_data.pop("created_at", None)
    update_data.pop("role", None)  # 👈 tránh user tự nâng quyền

    # nếu có password thì hash lại (nếu bạn có dùng auth)
    if "password" in update_data:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        update_data["hashed_password"] = pwd_context.hash(update_data.pop("password"))

    await collection.update_one(
        {"_id": obj_id},
        {"$set": update_data}
    )

    user = await collection.find_one({"_id": obj_id})

    if not user:
        return {"error": "User not found"}

    return serialize(user)


# DELETE USER
async def delete_user(user_id: str, collection):
    try:
        obj_id = ObjectId(user_id)
    except:
        return {"error": "Invalid user id"}

    result = await collection.delete_one({"_id": obj_id})

    if result.deleted_count == 0:
        return {"error": "User not found"}

    return {"message": "User deleted successfully"}