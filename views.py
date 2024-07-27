from http import HTTPStatus
from io import BytesIO

import pyqrcode
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from lnbits.core.models import User
from lnbits.decorators import require_admin_key
from lnbits.helpers import template_renderer
from lnurl import encode as lnurl_encode

from .crud import get_faucet_link

faucet_ext_generic = APIRouter()


def faucet_renderer():
    return template_renderer(["faucet/templates"])


@faucet_ext_generic.get("/", response_class=HTMLResponse)
async def index(request: Request, user: User = Depends(require_admin_key)):
    return faucet_renderer().TemplateResponse(
        "index.html", {"request": request, "user": user.dict()}
    )


@faucet_ext_generic.get("/{link_id}", response_class=HTMLResponse)
async def public(request: Request, link_id: str):
    link = await get_faucet_link(link_id)
    if not link:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Faucet does not exist."
        )
    url = str(request.url_for("faucet.api_lnurl_response"))
    return faucet_renderer().TemplateResponse(
        "public.html",
        {
            "request": request,
            "link": link.dict(),
            "lnurl": lnurl_encode(url),
        },
    )


@faucet_ext_generic.get("/img/{link_id}", response_class=StreamingResponse)
async def img(request: Request, link_id):
    link = await get_faucet_link(link_id, 0)
    if not link:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Withdraw link does not exist."
        )
    url = str(request.url_for("faucet.api_lnurl_response"))
    qr = pyqrcode.create(lnurl_encode(url))
    stream = BytesIO()
    qr.svg(stream, scale=3)
    stream.seek(0)

    async def _generator(stream: BytesIO):
        yield stream.getvalue()

    return StreamingResponse(
        _generator(stream),
        headers={
            "Content-Type": "image/svg+xml",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )
