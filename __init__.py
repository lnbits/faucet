import asyncio

from fastapi import APIRouter
from loguru import logger

from .crud import db
from .tasks import faucets_tick
from .views import faucet_generic_router
from .views_api import faucet_api_router
from .views_lnurl import faucet_lnurl_router

faucet_static_files = [
    {
        "path": "/faucet/static",
        "name": "faucet_static",
    }
]

faucet_ext: APIRouter = APIRouter(prefix="/faucet", tags=["faucet"])
faucet_ext.include_router(faucet_generic_router)
faucet_ext.include_router(faucet_api_router)
faucet_ext.include_router(faucet_lnurl_router)


scheduled_tasks: list[asyncio.Task] = []


def faucet_stop():
    for task in scheduled_tasks:
        try:
            task.cancel()
        except Exception as ex:
            logger.warning(ex)


def faucet_start():
    from lnbits.tasks import create_permanent_unique_task

    task = create_permanent_unique_task("ext_faucet_tick", faucets_tick)
    scheduled_tasks.append(task)


__all__ = ["faucet_ext", "faucet_static_files", "db", "faucet_start", "faucet_stop"]
