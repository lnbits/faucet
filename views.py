from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from lnbits.core.models import User
from lnbits.decorators import check_user_exists
from lnbits.helpers import template_renderer
from lnbits.settings import settings

from .crud import get_faucet
from .tasks import public_ws_listeners

faucet_generic_router = APIRouter()


def faucet_renderer():
    return template_renderer(["faucet/templates"])


@faucet_generic_router.get("/", response_class=HTMLResponse)
async def index(request: Request, user: User = Depends(check_user_exists)):
    return faucet_renderer().TemplateResponse(
        "index.html", {"request": request, "user": user.dict()}
    )


@faucet_generic_router.get("/{faucet_id}", response_class=HTMLResponse)
async def public(request: Request, faucet_id: str):
    faucet = await get_faucet(faucet_id)
    if not faucet:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Faucet does not exist."
        )
    return faucet_renderer().TemplateResponse(
        "display.html",
        {
            "request": request,
            "faucet_data": faucet.json(),
        },
    )

@faucet_generic_router.websocket("/{faucet_id}/ws")
async def websocket_faucet(websocket: WebSocket, faucet_id: str):
    faucet = await get_faucet(faucet_id)
    if not faucet:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Faucet does not exist."
        )
    await websocket.accept()
    public_ws_listeners[faucet_id] = websocket
    try:
        # Keep the connection alive
        while settings.lnbits_running:
            await websocket.receive_text()
    except WebSocketDisconnect:
        del public_ws_listeners[faucet_id]
        print("WebSocket connection closed", public_ws_listeners)
