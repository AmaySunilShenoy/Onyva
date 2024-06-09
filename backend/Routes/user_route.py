from fastapi import APIRouter, BackgroundTasks, WebSocket, WebSocketDisconnect, HTTPException, Request
from Services.user_service import update_user_email, edit_user_name, delete_user_name, toggle_route_to_fav
from Database_Connection.MongoDB import MongoDBConnection

router = APIRouter()
mongo = MongoDBConnection()

@router.post("/add_route_to_fav", tags=["User"])
async def add_route_to_fav_route( route_id: str, request: Request):
    result = toggle_route_to_fav( route_id, request)

#crud on users
@router.put("/edit-email", tags=["User"])
async def update_email_route(new_email: str, request: Request):
    try:
        user_id = request.state.user_id
        return update_user_email(user_id, new_email)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/edit-name", tags=["User"])
async def edit_name_route(name: str, request: Request):
    try:
        user_id = request.state.user_id
        return edit_user_name(user_id, name)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete-user-name", tags=["User"])
async def delete_user_name_route(request: Request):
    try:
        user_id = request.state.user_id
        return delete_user_name(user_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# viewing all the mongo data
@router.get("/all_users/", tags=["Admin"])
async def view_all_data_route():
    try:
        collection = mongo.get_collection("users")
        all_data = list(collection.find({}))

        for item in all_data:
            item['_id'] = str(item['_id'])

        return all_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))