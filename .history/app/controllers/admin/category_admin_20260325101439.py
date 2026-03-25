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
    """Xóa category, kiểm tra ràng buộc Place"""
    try:
        obj_id = ObjectId(category_id)
    except:
        return False, "Invalid category id"

    # Kiểm tra có Place nào đang dùng category không
    place_using = await place_collection.count_documents({"category_id": category_id})
    if place_using > 0:
        return False, "Cannot delete: Category is used by some places"

    result = await collection.delete_one({"_id": obj_id})
    if result.deleted_count == 0:
        return False, "Category not found"

    return True, None