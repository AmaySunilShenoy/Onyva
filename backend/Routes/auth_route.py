from fastapi import FastAPI, APIRouter, HTTPException
from Services.auth_service import create_user

router = APIRouter()

@router.post("/create/", tags=["Users"])
async def create_user_route(email: str, password: str):
    try:
        user_id =  create_user(email, password)
        return {"user_id": user_id, "message": "User created successfully"}
    except HTTPException as e:
        raise e

# @router.get("/users/login/", tags=["Users"])
# async def get_user(user):
#     user_data = get_user(user)
#     return user_data
