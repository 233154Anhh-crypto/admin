from fastapi import APIRouter, Depends
from bson import ObjectId
from app.models.place_model import PlaceCreate,PlaceUpdate
from app.controllers.admin import place_admin_controller as admin_ctrl
from dependencies import get_place_collection

router = APIRouter(prefix="/places", tags=["Admin - Places"])

@router.get("/")
async def get_all_places(
    collection=Depends(get_place_collection)
):
    return await admin_ctrl.get_places(collection)

@router.post("/create", response_model=dict)
async def create_place(
    data: PlaceCreate,
    collection=Depends(get_place_collection)
):
    return await admin_ctrl.create_place(data, collection)
@router.put("/update/{place_id}")
async def update_place(
    place_id: str,
    data: PlaceUpdate,
    collection=Depends(get_place_collection)
):
    return await admin_ctrl.update_place(place_id, data, collection)


# DELETE PLACE
@router.delete("/delete/{place_id}")
async def delete_place(
    place_id: str,
    collection=Depends(get_place_collection)
):
    return await admin_ctrl.delete_place(place_id, collection)