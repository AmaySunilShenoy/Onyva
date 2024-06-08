from fastapi import APIRouter, BackgroundTasks, WebSocket, WebSocketDisconnect, HTTPException
from Services.subscription_service import (
    subscribe_to_route,
    handle_messages,
    get_subscriptions,
    publish_crime_report,
    get_reports_for_subscriptions,
    get_all_reports,
)

router = APIRouter()

@router.get("/subscribe", tags=["Ligne"])
async def subscribe_route_updates(email: str, route_id: str):
    result = subscribe_to_route(route_id, email)
    return result

@router.get("/subscriptions", tags=["Ligne"])
async def subscriptions(email: str):
    subscriptions = get_subscriptions(email)
    return {"subscriptions": list(subscriptions)}

@router.websocket("/ws/{email}")
async def websocket_endpoint(websocket: WebSocket, email: str):
    await websocket.accept()
    try:
        await handle_messages(email, websocket)
    except WebSocketDisconnect:
        print(f"Client {email} disconnected")
    except Exception as e:
        print(f"Error in websocket for {email}: {e}")


@router.get("/publish", tags=["Ligne"])
async def crime_report(email: str, route_id: str, crime_report: str):
    result = publish_crime_report(email, route_id, crime_report)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.get("/reports", tags=["Ligne"])
async def get_subscribed_reports(email: str):
    reports = get_reports_for_subscriptions(email)
    return {"reports": reports}

@router.get("/reports/all", tags=["Admin"])
async def get_all_crime_reports():
    reports = get_all_reports()
    return {"reports": reports}

