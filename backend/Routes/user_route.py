from Services.user_service import toggle_route_to_fav
from fastapi import APIRouter, Request, Header

router = APIRouter()

@router.post("/add_route_to_fav", tags=["User"])
async def add_route_to_fav_route( route_id: str, request: Request):
    result = toggle_route_to_fav( route_id, request)
    return result