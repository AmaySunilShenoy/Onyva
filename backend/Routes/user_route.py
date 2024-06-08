from fastapi import APIRouter, BackgroundTasks, WebSocket, WebSocketDisconnect, HTTPException
from Services.user_service import (
    subscribe_to_route,
    handle_messages,
    get_subscriptions,
    publish_crime_report,
    get_reports_for_subscriptions,
    get_all_reports,
)

router = APIRouter()

@router.get("/subscribe", tags=["User"])
async def subscribe_route_updates(email: str, route_id: str):
    result = subscribe_to_route(route_id, email)
    return result

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

@router.get("/publish", tags=["User"])
async def crime_report(email: str, route_id: str, crime_report: str):
    result = publish_crime_report(email, route_id, crime_report)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.get("/reports", tags=["User"])
async def get_subscribed_reports(email: str):
    reports = get_reports_for_subscriptions(email)
    return {"reports": reports}

@router.get("/reports/all", tags=["Admin"])
async def get_all_crime_reports():
    reports = get_all_reports()
    return {"reports": reports}

