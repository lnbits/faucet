import datetime
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from lnbits.core.models import User, WalletTypeInfo
from lnbits.decorators import check_user_exists, require_admin_key

from .crud import (
    create_faucet,
    delete_faucet,
    get_faucet,
    get_faucets,
    update_faucet,
)
from .models import CreateFaucet, Faucet

faucet_api_router = APIRouter(prefix="/api/v1")


async def _validate_faucet_data(data: CreateFaucet):
    if data.start_time > data.end_time:
        raise HTTPException(
            detail="Start time must be before end time.",
            status_code=HTTPStatus.BAD_REQUEST,
        )
    now = int(datetime.datetime.now().timestamp())
    if data.start_time.timestamp() < now:
        raise HTTPException(
            detail="Start time must be in the future.",
            status_code=HTTPStatus.BAD_REQUEST,
        )


@faucet_api_router.get("")
async def api_faucets_get(user: User = Depends(check_user_exists)):
    faucets = await get_faucets(user.wallet_ids)
    return faucets


@faucet_api_router.get("/{faucet_id}", status_code=HTTPStatus.OK)
async def api_faucet_get(
    faucet_id: str, user: User = Depends(check_user_exists)
) -> Faucet:
    faucet = await get_faucet(faucet_id)
    if not faucet:
        raise HTTPException(
            detail="Faucet does not exist.", status_code=HTTPStatus.NOT_FOUND
        )

    if faucet.wallet not in user.wallet_ids:
        raise HTTPException(detail="Not your Faucet.", status_code=HTTPStatus.FORBIDDEN)
    return faucet


@faucet_api_router.post("", status_code=HTTPStatus.CREATED)
async def api_faucet_create(
    data: CreateFaucet,
    key_type: WalletTypeInfo = Depends(require_admin_key),
) -> Faucet:
    if key_type.wallet.id != data.wallet:
        raise HTTPException(detail="Not your wallet.", status_code=HTTPStatus.FORBIDDEN)
    await _validate_faucet_data(data)
    return await create_faucet(data)

@faucet_api_router.put("/{faucet_id}")
async def api_faucet_update(
    faucet_id: str,
    data: CreateFaucet,
    wallet: WalletTypeInfo = Depends(require_admin_key),
):
    faucet = await get_faucet(faucet_id)
    if not faucet:
        raise HTTPException(
            detail="Faucet does not exist.", status_code=HTTPStatus.NOT_FOUND
        )
    if faucet.wallet != wallet.wallet.id:
        raise HTTPException(detail="Not your Wallet.", status_code=HTTPStatus.FORBIDDEN)
    await _validate_faucet_data(data)
    for key, val in data.dict().items():
        setattr(faucet, key, val)
    await update_faucet(faucet)


@faucet_api_router.delete("/{faucet_id}", status_code=HTTPStatus.OK)
async def api_faucet_delete(
    faucet_id: str, wallet: WalletTypeInfo = Depends(require_admin_key)
):
    faucet = await get_faucet(faucet_id)
    if not faucet:
        raise HTTPException(
            detail="Faucet does not exist.", status_code=HTTPStatus.NOT_FOUND
        )
    if faucet.wallet != wallet.wallet.id:
        raise HTTPException(detail="Not your Faucet.", status_code=HTTPStatus.FORBIDDEN)
    await delete_faucet(faucet_id)
