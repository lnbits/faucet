from datetime import datetime
from http import HTTPStatus
from typing import Callable

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from lnbits.core.crud import get_wallet
from lnbits.core.services import pay_invoice
from loguru import logger

from .crud import (
    get_faucet,
    get_faucet_secret,
    update_faucet,
    update_faucet_secret,
)
from .models import Faucet, FaucetSecret
from .tasks import send_websocket_messages


class LnurlErrorResponseHandler(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def lnurl_route_handler(request: Request) -> Response:
            try:
                response = await original_route_handler(request)
                return response
            except HTTPException as exc:
                logger.debug(f"HTTPException: {exc}")
                response = JSONResponse(
                    status_code=200,
                    content={"status": "ERROR", "reason": f"{exc.detail}"},
                )
                return response
            except Exception as exc:
                logger.error("Unknown Error:", exc)
                response = JSONResponse(
                    status_code=200,
                    content={
                        "status": "ERROR",
                        "reason": f"UNKNOWN ERROR: {exc!s}",
                    },
                )
                return response

        return lnurl_route_handler


faucet_lnurl_router = APIRouter(prefix="/api/v1/lnurl")
faucet_lnurl_router.route_class = LnurlErrorResponseHandler


async def _validate_faucet(k1: str) -> tuple[Faucet, FaucetSecret]:
    secret = await get_faucet_secret(k1)
    if not secret:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="k1 is wrong.")
    faucet = await get_faucet(secret.faucet_id)
    if not faucet:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="faucet does not exist."
        )
    if (
        faucet.end_time.timestamp() < datetime.now().timestamp()
        or faucet.start_time.timestamp() > datetime.now().timestamp()
    ):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="faucet is closed."
        )
    if faucet.current_k1 != k1:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="k1 is wrong.")
    wallet = await get_wallet(faucet.wallet)
    if not wallet:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="wallet does not exist."
        )

    if wallet.balance_msat < faucet.withdrawable:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="insufficient balance."
        )
    return faucet, secret


@faucet_lnurl_router.get(
    "/{k1}",
    response_class=JSONResponse,
    name="faucet.api_lnurl_response",
)
async def api_lnurl_response(request: Request, k1: str):
    faucet, secret = await _validate_faucet(k1)
    url = request.url_for("faucet.api_lnurl_callback")
    amount_msat = 100 * 1000
    return {
        "tag": "withdrawRequest",
        "callback": str(url),
        "k1": secret.k1,
        "minWithdrawable": amount_msat,
        "maxWithdrawable": amount_msat,
        "defaultDescription": faucet.description or faucet.title,
    }


@faucet_lnurl_router.get(
    "/cb/",
    response_class=JSONResponse,
    name="faucet.api_lnurl_callback",
)
async def api_lnurl_callback(k1: str, pr: str):
    faucet, secret = await _validate_faucet(k1)
    await pay_invoice(
        wallet_id=faucet.wallet,
        payment_request=pr,
        max_sat=faucet.withdrawable,
        extra={"tag": "faucet", "faucet_id": faucet.id},
    )
    faucet.current_k1 = None
    faucet.lnurl = None
    faucet.current_use += 1
    await update_faucet(faucet)
    secret.used_time = datetime.now()
    await update_faucet_secret(secret)
    await send_websocket_messages(faucet)
    return {"status": "OK"}
