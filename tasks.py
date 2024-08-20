import asyncio
import datetime

from fastapi import WebSocket
from lnbits.settings import settings
from loguru import logger

from .crud import get_active_faucets
from .models import Faucet


public_ws_listeners: dict[str, WebSocket] = {}


async def faucets_tick():
    while settings.lnbits_running:
        active_faucets = await get_active_faucets()
        if len(active_faucets) > 0:
            logger.debug(f"Faucet tick, active_faucets: {len(active_faucets)}")
        for faucet in active_faucets:
            logger.debug(f"faucets_tick ({faucet.id})")
            # faucet.tick()
            now = datetime.datetime.now().timestamp()
            if now >= faucet.next_tick.timestamp():
                faucet.next_tick = datetime.datetime.fromtimestamp(
                    now + faucet.interval
                )
                logger.debug(
                    f"faucets_tick ({faucet.id}) - next_tick: {faucet.next_tick}"
                )
                # faucet.current_k1 = get_next_k1(faucet.id)
            # await update_faucet(faucet)
            # await send_websocket_messages(faucet)
        await asyncio.sleep(15)


async def send_websocket_messages(faucet: Faucet):
    for faucet_id, websocket in public_ws_listeners.items():
        if faucet_id == faucet.id:
            logger.debug(f"send_websocket_messages ({faucet.id})")
            await websocket.send_json(
                {
                    "current_k1": faucet.current_k1,
                    "next_tick": faucet.next_tick,
                }
            )
