from fastapi import APIRouter, Depends
from app.controllers.admin import category_admin as ctrl
from app.models.category import CategoryCreate, CategoryUpdate
from dependencies import get_category_collection,get_place_collection

router = APIRouter(prefix="/categories", tags=["Admin Category"])

@router.get("/")
async def list_categories(collection=Depends(get_category_collection)):
    return await ctrl.get_categories(collection)

@router.post("/create")
async def create_category(data: CategoryCreate, collection=Depends(get_category_collection)):
    return await ctrl.create_category(data, collection)

@router.put("/update/{category_id}")
async def update_category(category_id: str, data: CategoryUpdate, collection=Depends(get_category_collection)):
    updated = await ctrl.update_category(category_id, data, collection)
    if not updated:
        return {"error": "Update failed"}
    return updated

@router.delete("/delete/{category_id}")
async def delete_category(category_id: str,
                          collection=Depends(get_category_collection),
                          place_collection=Depends(get_place_collection)):
    success, msg = await ctrl.delete_category(category_id, collection, place_collection)
    if not success:
        return {"error": msg}
    return {"message": "Category deleted"}


@router.get("/{category_id}/places")
async def get_category_places(category_id: str,
                              place_collection=Depends(get_place_collection)):
    return await ctrl.get_places_by_category(category_id, place_collection)