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