from fastapi import APIRouter, HTTPException, Request, Depends, Query
from Services.user_service import update_user_email, edit_user_name, delete_user_name, toggle_route_to_fav, delete_user
from Database_Connection.MongoDB import MongoDBConnection
from typing import Optional


router = APIRouter()
mongo = MongoDBConnection()

async def get_user_id(request: Request):
    user_id = request.state.user_id
    if user_id is None:
        raise HTTPException(status_code=400, detail="Session not established. Please provide a user_id in the header.")
    return user_id

@router.post("/add_route_to_fav", tags=["User"])
async def add_route_to_fav_route( route_id: str, request: Request, q: Optional[str] = Query(None, )):
    """
    Add a route to the user's favourite routes (MongoDB)
    """
    result = toggle_route_to_fav( route_id, request)
    return result

#crud on users
@router.put("/edit-email", tags=["User"])
async def update_email_route(new_email: str, user_id : str = Depends(get_user_id), q: Optional[str] = Query(None, )):
    """
    Update the email of the user with the new email provided
    """
    try:
        return update_user_email(user_id, new_email)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.put("/edit-name", tags=["User"])
async def edit_name_route(name: str, user_id : str = Depends(get_user_id), q: Optional[str] = Query(None, )):
    """
    Edit a name to the user with the name provided
    """
    try:
        return edit_user_name(user_id, name)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete-user-name", tags=["User"])
async def delete_user_name_route(user_id : str = Depends(get_user_id), q: Optional[str] = Query(None,  )):
    """
    Delete the name of the user
    """
    try:
        return delete_user_name(user_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/delete-user", tags=["User"])
async def delete_user_route(user_id : str = Depends(get_user_id), q: Optional[str] = Query(None,  )):
    """
    Delete the user
    """
    try:
        return delete_user(user_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# viewing all the mongo data
@router.get("/all_users/", tags=["Admin"])
async def view_all_data_route(q: Optional[str] = Query(None,  )):
    """
    Get all the users data from the MongoDB **(Only for Admin)**
    """
    try:
        collection = mongo.get_collection("users")
        all_data = list(collection.find({}))

        for item in all_data:
            item['_id'] = str(item['_id'])

        return all_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))