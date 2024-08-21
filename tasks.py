import asyncio
import datetime

from fastapi import WebSocket
from fastapi.websockets import WebSocketState
from lnbits.settings import settings
from lnurl import encode as lnurl_encode
from loguru import logger

from .crud import get_active_faucets, get_next_faucet_secret, update_faucet
from .models import Faucet

public_ws_listeners: dict[str, list[WebSocket]] = {}


async def faucets_tick():
    while settings.lnbits_running:
        active_faucets = await get_active_faucets()
        if len(active_faucets) > 0:
            logger.debug(f"Faucet tick, active_faucets: {len(active_faucets)}")
        for faucet in active_faucets:
            await faucet_tick(faucet)
        await asyncio.sleep(15)


async def faucet_tick(faucet: Faucet):
    now = datetime.datetime.now().timestamp()
    if now <= faucet.next_tick.timestamp():
        return

    faucet.next_tick = datetime.datetime.fromtimestamp(
        now + faucet.interval
    )
    faucet = await update_secret(faucet)
    await update_faucet(faucet)
    await send_websocket_messages(faucet)
    logger.debug(
        f"faucets_tick ({faucet.id}) "
        f"- next_tick: {faucet.next_tick} "
        f"- current_k1: {faucet.current_k1 or 'used'} "
    )


async def update_secret(faucet: Faucet) -> Faucet:
    secret = await get_next_faucet_secret(faucet.id)
    if not secret:
        logger.debug("No more faucet secrets found, skipping...")
        faucet.current_k1 = None
        faucet.lnurl = None
        faucet.current_use = faucet.uses
        return faucet
    if not faucet.current_k1:
        logger.debug(f"Updating faucet secret for {faucet.id}...")
        faucet.current_use += 1
    url = f"{settings.lnbits_baseurl.rstrip('/')}/faucet/api/v1/lnurl/{secret.k1}"
    faucet.current_k1 = secret.k1
    faucet.lnurl = str(lnurl_encode(url))
    return faucet


async def send_websocket_messages(faucet: Faucet):
    for faucet_id, websockets in public_ws_listeners.items():
        if faucet_id == faucet.id:
            for websocket in websockets:
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_json({
                        "current_use": faucet.current_use,
                        "current_k1": faucet.current_k1,
                        "lnurl": faucet.lnurl,
                        "next_tick": faucet.next_tick.isoformat(),
                    })
