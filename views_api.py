from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from lnbits.core.models import User, WalletTypeInfo
from lnbits.decorators import check_user_exists, require_admin_key

from .crud import (
    create_faucet,
    delete_faucet,
    get_faucet,
    get_faucets,
)
from .models import CreateFaucet, Faucet

faucet_api_router = APIRouter(prefix="/api/v1")


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
    return await create_faucet(data)


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
