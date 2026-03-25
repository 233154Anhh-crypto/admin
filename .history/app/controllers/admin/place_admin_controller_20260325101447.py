import os
from dotenv import load_dotenv
from datetime import datetime
from bson import ObjectId
from app.models.place_model import PlaceCreate, PlaceUpdate

load_dotenv()

# Base URL để frontend dùng hiển thị ảnh
BASE_IMAGE_URL = os.getenv("BASE_IMAGE_URL") or "/static/image/"

def serialize(place):
    """Chuyển place từ database sang dict trả frontend"""
    return {
        "id": str(place["_id"]),
        "name": place["name"],
        "description": place.get("description"),
        "address": place["address"],
        "city": place["city"],
        "category_id": place["category_id"],
        # Trả thumbnail chỉ dạng /static/image/filename.jpg
        "thumbnail": f"{BASE_IMAGE_URL}{place['thumbnail']}" if place.get("thumbnail") else None,
        "created_at": place["created_at"]
    }

async def get_places(collection):
    """Lấy tất cả place"""
    places = []
    async for place in collection.find():
        places.append(serialize(place))
    return places

async def create_place(data: PlaceCreate, collection, category_collection):
    """Tạo place mới"""
    place = {
        "name": data.name,
        "description": data.description,
        "address": data.address,
        "city": data.city,
        "category_id": data.category_id,
        "thumbnail": data.thumbnail,  # chỉ tên file
        "created_at": datetime.utcnow()
    }

    result = await collection.insert_one(place)
    place["_id"] = result.inserted_id
    place_id = str(result.inserted_id)

    # Thêm place_id vào category's places
    await category_collection.update_one(
        {"_id": ObjectId(data.category_id)},
        {"$push": {"places": place_id}}
    )

    return serialize(place)

async def update_place(place_id: str, data: PlaceUpdate, collection):
    """Cập nhật place và xử lý xóa file ảnh cũ nếu thay đổi"""
    try:
        obj_id = ObjectId(place_id)
    except:
        return None

    place = await collection.find_one({"_id": obj_id})
    if not place:
        return None

    update_data = {k: v for k, v in data.dict().items() if v is not None}

    # Nếu cập nhật thumbnail mới
    if "thumbnail" in update_data:
        old_thumbnail = place.get("thumbnail")
        if old_thumbnail:
            old_file = os.path.join("app", "static", "image", os.path.basename(old_thumbnail))
            if os.path.exists(old_file):
                os.remove(old_file)
        # Chỉ lưu tên file mới
        update_data["thumbnail"] = os.path.basename(update_data["thumbnail"])

    if not update_data:
        return None

    result = await collection.update_one({"_id": obj_id}, {"$set": update_data})
    if result.matched_count == 0:
        return None

    updated_place = await collection.find_one({"_id": obj_id})
    return serialize(updated_place)

async def delete_place(place_id: str, collection):
    """Xóa place và file ảnh cũ"""
    try:
        obj_id = ObjectId(place_id)
    except:
        return False

    place = await collection.find_one({"_id": obj_id})
    if not place:
        return False

    result = await collection.delete_one({"_id": obj_id})
    if result.deleted_count == 0:
        return False

    # Xóa file ảnh cũ an toàn
    if place.get("thumbnail"):
        # Lấy chỉ tên file
        filename = os.path.basename(place["thumbnail"])
        file_path = os.path.join("app", "static", "image", filename)
        if os.path.exists(file_path):
            os.remove(file_path)

    return True