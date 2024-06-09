from fastapi import FastAPI, APIRouter, HTTPException, Form
from Services.auth_service import create_user, get_user

router = APIRouter()

@router.post("/create/", tags=["Authentication"])
async def create_user_route(email: str, password: str):
    try:
        user_token =  create_user(email, password)
        return {"User": user_token, "message": "User created successfully"}
        # logging the user in
        
    except HTTPException as e:
        raise e

@router.post("/users/login/", tags=["Authentication"])
async def get_user_route(email: str , password: str ):
    try:
        user_data = get_user(email, password)
        return {"User": user_data, "message": "User logged in successfully"}
    except HTTPException as e:
        raise e


