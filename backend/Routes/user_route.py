from Services.user_service import add_route_to_fav
from fastapi import APIRouter

router = APIRouter()

@router.post("/add_route_to_fav", tags=["User"])
async def add_route_to_fav_route(user_id: str, route_id: str):
    result = add_route_to_fav(user_id, route_id)
    return result