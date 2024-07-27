from fastapi import APIRouter

from .crud import db
from .views import faucet_ext_generic
# from .views_api import faucet_ext_api
# from .views_lnurl import faucet_ext_lnurl

faucet_static_files = [
    {
        "path": "/faucet/static",
        "name": "faucet_static",
    }
]

faucet_ext: APIRouter = APIRouter(prefix="/faucet", tags=["faucet"])
faucet_ext.include_router(faucet_ext_generic)
# faucet_ext.include_router(faucet_ext_api)
# faucet_ext.include_router(faucet_ext_lnurl)

__all__ = ["faucet_ext", "faucet_static_files", "db"]
