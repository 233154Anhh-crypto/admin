from fastapi import APIRouter, Depends
from app.controllers.admin import admin_user_controller as user_ctrl
from app.models.user import UserUpdate
from dependencies import get_user_collection

router = APIRouter()


# GET ALL USERS
@router.get("/users")
async def get_users(collection=Depends(get_user_collection)):
    return await user_ctrl.get_users(collection)


# CREATE USER
@router.post("/users")
async def create_user(
    data: UserUpdate,
    collection=Depends(get_user_collection)
):
    return await user_ctrl.create_user(data, collection)


# GET ONE USER
@router.get("/users/{user_id}")
async def get_user(user_id: str, collection=Depends(get_user_collection)):
    return await user_ctrl.get_user(user_id, collection)


# UPDATE USER
@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    data: UserUpdate,
    collection=Depends(get_user_collection)
):
    return await user_ctrl.update_user(user_id, data, collection)


# DELETE USER
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    collection=Depends(get_user_collection)
):
    return await user_ctrl.delete_user(user_id, collection)