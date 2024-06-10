from fastapi import APIRouter, BackgroundTasks, WebSocket, WebSocketDisconnect, HTTPException, Query, Request, Depends
from Services.subscription_service import (
    toggle_subscribtion_to_route,
    handle_messages,
    get_subscriptions,
    publish_crime_report,
    get_reports_for_all_subscriptions,
    get_reports_for_route,
    get_all_reports,
)
from typing import Optional

router = APIRouter()

async def get_user_id(request: Request):
    user_id = request.state.user_id
    if user_id is None:
        raise HTTPException(status_code=400, detail="Session not established. Please provide a user_id in the header.")
    return user_id

@router.post("/subscribe", tags=["Ligne"])
async def subscribe_route_updates(route_id: str,user_id : str = Depends(get_user_id)):
    """
    Subscribe to route updates for a given route_id / Unsubscribe from route updates if already subscribed
    """

    result = toggle_subscribtion_to_route(route_id, user_id)
    return result

@router.get("/subscriptions", tags=["Ligne"])
async def subscriptions(user_id : str = Depends(get_user_id)):
    """
    Get all the subscriptions for a user
    """
  
    subscriptions = get_subscriptions(user_id)
    return {"subscriptions": list(subscriptions)}

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    try:
        await handle_messages(user_id, websocket)
    except WebSocketDisconnect:
        print(f"Client {user_id} disconnected")
    except Exception as e:
        print(f"Error in websocket for {user_id}: {e}")


@router.post("/publish", tags=["Ligne"])
async def crime_report(route_id: str, crime_report: str,user_id : str = Depends(get_user_id)):
    """
    Publish a crime report for a given route_id (which will be sent to all subscribers of the route and stored in redis for later retrieval)
    """

    result = publish_crime_report(user_id, route_id, crime_report)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.get("/report/{route_id}", tags=["Ligne"])
async def get_subscribed_reports(route_id: str):
    """
    Get all the crime reports for a given route
    """

    reports = get_reports_for_route(route_id)
    return {"reports": reports}

@router.get("/reports", tags=["Ligne"])
async def get_subscribed_reports(user_id : str = Depends(get_user_id)):
    """
    Get all the crime reports for the routes the user is subscribed to
    """

    reports = get_reports_for_all_subscriptions(user_id)
    return {"reports": reports}

@router.get("/reports/all", tags=["Ligne"])
async def get_all_crime_reports():
    """
    Get all the crime reports for all routes
    """
   
    reports = get_all_reports()
    return {"reports": reports}

