from fastapi import APIRouter, BackgroundTasks, WebSocket, WebSocketDisconnect, HTTPException
from Services.user_service import subscribe_to_route, handle_messages, get_subscriptions, publish_crime_report, update_user_email, edit_user_name, delete_user_name
from Database_Connection.MongoDB import MongoDBConnection

router = APIRouter()

@router.post("/add_route_to_fav", tags=["User"])
async def add_route_to_fav_route( route_id: str, request: Request):
    result = toggle_route_to_fav( route_id, request)

mongo = MongoDBConnection()
@router.get("/subscribe", tags=["User"])
async def subscribe_route_updates(email: str, route_id: str):
    result = subscribe_to_route(route_id, email)
    return {"success": result}

@router.get("/subscriptions", tags=["User"])
async def subscriptions(email: str):
    subscriptions = get_subscriptions(email)
    return {"subscriptions": list(subscriptions)}

@router.websocket("/ws/{email}")
async def websocket_endpoint(websocket: WebSocket, email: str):
    await websocket.accept()
    background_tasks = BackgroundTasks()
    background_tasks.add_task(handle_messages, email, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        print(f"Client {email} disconnected")

# publish crime report
@router.get("/publish", tags=["User"])
async def crime_report(email: str, route_id: str, crime_report: str):
    result = publish_crime_report(email, route_id, crime_report)
    return result


#crud on users
@router.put("/edit-email/", tags=["User"])
async def update_email_route(user_id: str, new_email: str):
    try:
        return update_user_email(user_id, new_email)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/edit-name/", tags=["User"])
async def edit_name_route(user_id: str, name: str):
    try:
        return edit_user_name(user_id, name)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete-user-name/{user_id}", tags=["User"])
async def delete_user_name_route(user_id: str):
    try:
        return delete_user_name(user_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# viewing all the mongo data
@router.get("/view-all-data/", tags=["MongoDB"])
async def view_all_data_route():
    try:
        collection = mongo.get_collection("users")
        all_data = list(collection.find({}))

        for item in all_data:
            item['_id'] = str(item['_id'])

        return all_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))