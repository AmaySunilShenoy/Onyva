from fastapi import FastAPI, APIRouter, HTTPException, Form
from Services.auth_service import create_user, get_user

router = APIRouter()

@router.post("/create/", tags=["Authentication"])
async def create_user_route(email: str, password: str):
    try:
        user_id =  create_user(email, password)
        return {"user_id": user_id, "message": "User created successfully"}
    except HTTPException as e:
        raise e

@router.post("/users/login/", tags=["Authentication"])
async def get_user_route(email: str , password: str ):
    try:
        user_data = get_user(email, password)
        return user_data
    except HTTPException as e:
        raise e


