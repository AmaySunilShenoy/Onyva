from fastapi import FastAPI, APIRouter, HTTPException, Form, Query
from Services.auth_service import create_user, get_user
from typing import Optional

router = APIRouter()

@router.post("/create/", tags=["Authentication"])
async def create_user_route(email: str, password: str):
    """
    Create a new user in the database with the email and password provided
    """
    try:
        # creating the user
        user_token =  create_user(email, password)

        # returning user token (with refresh token and access token)
        return {"User": user_token, "message": "User created successfully"}
        
    except HTTPException as e:
        raise e

@router.post("/users/login/", tags=["Authentication"])
async def get_user_route(email: str , password: str ):
    """
    Get user from the database with the email and password provided
    """
    try:

        # getting the user
        user_data = get_user(email, password)

        # returning user data
        return {"User": user_data, "message": "User logged in successfully"}
    except HTTPException as e:
        raise e


