from datetime import datetime
from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from lnbits.core.services import pay_invoice
from lnbits.lnurl import LnurlErrorResponseHandler

from .crud import (
    get_faucet,
    get_faucet_secret,
)

faucet_lnurl_router = APIRouter(prefix="/api/v1/lnurl")
faucet_lnurl_router.route_class = LnurlErrorResponseHandler


@faucet_lnurl_router.get(
    "/{k1}",
    response_class=JSONResponse,
    name="faucet.api_lnurl_response",
)
async def api_lnurl_response(request: Request, k1: str):
    secret = await get_faucet_secret(k1)
    if not secret:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="k1 is wrong.")
    faucet = await get_faucet(secret.faucet_id)
    if not faucet:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="faucet does not exist."
        )
    if faucet.current_k1 != k1:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="k1 is wrong.")
    url = str(request.url_for("withdraw.api_lnurl_callback", k1=k1))
    amount_msat = 100 * 1000
    return {
        "tag": "withdrawRequest",
        "callback": url,
        "k1": k1,
        "minWithdrawable": amount_msat,
        "maxWithdrawable": amount_msat,
        "defaultDescription": faucet.description or faucet.title,
    }


@faucet_lnurl_router.get(
    "/cb/{faucet_id}",
    name="faucet.api_lnurl_callback",
    response_class=JSONResponse,
)
async def api_lnurl_callback(
    faucet_id: str,
    k1: str,
    pr: str,
):
    faucet = await get_faucet(faucet_id)
    if not faucet:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="faucet does not exist."
        )
    secret = await get_faucet_secret(k1)
    if not secret or secret.k1 != faucet.current_k1:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="k1 is wrong.")

    now = int(datetime.now().timestamp())

    if now < link.open_time:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"wait link open_time {link.open_time - now} seconds.",
        )

    if not id_unique_hash and link.is_unique:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="id_unique_hash is required for this link.",
        )

    if id_unique_hash:
        if check_unique_link(link, id_unique_hash):
            await remove_unique_withdraw_link(link, id_unique_hash)
        else:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="withdraw not found."
            )

    # Create a record with the id_unique_hash or unique_hash, if it already exists,
    # raise an exception thus preventing the same LNURL from being processed twice.
    try:
        await create_hash_check(id_unique_hash or unique_hash, k1)
    except Exception as exc:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="LNURL already being processed."
        ) from exc

    try:
        payment_hash = await pay_invoice(
            wallet_id=link.wallet,
            payment_request=pr,
            max_sat=link.max_withdrawable,
            extra={"tag": "withdraw", "withdrawal_link_id": link.id},
        )
        await increment_withdraw_link(link)
        # If the payment succeeds, delete the record with the unique_hash.
        # TODO: we delete this now: "If it has unique_hash, do not delete to prevent
        # the same LNURL from being processed twice."
        await delete_hash_check(id_unique_hash or unique_hash)
        return {"status": "OK"}
    except Exception as exc:
        # If payment fails, delete the hash stored so another attempt can be made.
        await delete_hash_check(id_unique_hash or unique_hash)
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=f"withdraw not working. {exc!s}"
        ) from exc
