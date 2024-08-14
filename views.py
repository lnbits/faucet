from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from lnbits.core.models import User
from lnbits.decorators import check_user_exists
from lnbits.helpers import template_renderer

from .crud import get_faucet

faucet_ext_generic = APIRouter()


def faucet_renderer():
    return template_renderer(["faucet/templates"])


@faucet_ext_generic.get("/", response_class=HTMLResponse)
async def index(request: Request, user: User = Depends(check_user_exists)):
    return faucet_renderer().TemplateResponse(
        "index.html", {"request": request, "user": user.dict()}
    )


@faucet_ext_generic.get("/{faucet_id}", response_class=HTMLResponse)
async def public(request: Request, faucet_id: str):
    faucet = await get_faucet(faucet_id)
    if not faucet:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Faucet does not exist."
        )
    return faucet_renderer().TemplateResponse(
        "public.html",
        {
            "request": request,
            "faucet": faucet.dict(),
        },
    )
