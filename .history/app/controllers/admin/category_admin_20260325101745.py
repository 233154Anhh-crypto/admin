import os
from datetime import datetime
from bson import ObjectId
from app.models.category import CategoryCreate, CategoryUpdate

def serialize(category):
    """Chuyển category từ DB sang dict trả frontend"""
    return {
        "id": str(category["_id"]),
        "name": category["name"],
        "description": category.get("description"),
        "places": category.get("places", []),
        "created_at": category.get("created_at")
    }

async def get_categories(collection):
    categories = []
    async for cat in collection.find():
        categories.append(serialize(cat))
    return categories

async def create_category(data: CategoryCreate, collection):
    category = {
        "name": data.name,
        "description": data.description,
        "places": [],
        "created_at": datetime.utcnow()
    }
    result = await collection.insert_one(category)
    category["_id"] = result.inserted_id
    return serialize(category)

async def update_category(category_id: str, data: CategoryUpdate, collection):
    try:
        obj_id = ObjectId(category_id)
    except:
        return None

    update_data = {k: v for k, v in data.dict().items() if v is not None}
    if not update_data:
        return None

    result = await collection.update_one({"_id": obj_id}, {"$set": update_data})
    if result.matched_count == 0:
        return None

    updated_category = await collection.find_one({"_id": obj_id})
    return serialize(updated_category)

async def delete_category(category_id: str, collection, place_collection):
    """Xóa category và tất cả places trong nó"""
    try:
        obj_id = ObjectId(category_id)
    except:
        return False, "Invalid category id"

    category = await collection.find_one({"_id": obj_id})
    if not category:
        return False, "Category not found"

    # Xóa tất cả places trong category
    places = category.get("places", [])
    for place_id in places:
        try:
            place_obj_id = ObjectId(place_id)
            place = await place_collection.find_one({"_id": place_obj_id})
            if place and place.get("thumbnail"):
                filename = os.path.basename(place["thumbnail"])
                file_path = os.path.join("app", "static", "image", filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
            await place_collection.delete_one({"_id": place_obj_id})
        except:
            pass  # Ignore errors

    # Xóa category
    result = await collection.delete_one({"_id": obj_id})
    if result.deleted_count == 0:
        return False, "Category not found"

    return True, None


async def get_places_by_category(category_id: str, place_collection):
    """Lấy danh sách place theo category"""
    places = []
    async for place in place_collection.find({"category_id": category_id}):
        places.append({
            "id": str(place.get("_id")),
            "name": place.get("name"),
            "description": place.get("description"),
            "address": place.get("address"),
            "city": place.get("city"),
            "category_id": place.get("category_id"),
            "thumbnail": place.get("thumbnail"),
            "created_at": place.get("created_at"),
        })
    return places