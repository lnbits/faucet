import datetime
from typing import Optional

from lnbits.db import Database
from lnbits.helpers import insert_query, update_query, urlsafe_short_hash

from .models import CreateFaucet, Faucet, FaucetSecret

db = Database("ext_faucet")


async def create_faucet(data: CreateFaucet) -> Faucet:
    faucet_id = urlsafe_short_hash()
    k1 = ""
    for _ in range(data.uses):
        k1 = urlsafe_short_hash()
        await create_faucet_secret(FaucetSecret(k1=k1, faucet_id=faucet_id))

    faucet = Faucet(id=faucet_id, next_tick=data.start_time, **data.dict())
    await db.execute(
        insert_query("faucet.faucet", faucet),
        (*faucet.dict().values(),),
    )

    return faucet


async def delete_faucet(faucet_id: str) -> None:
    await db.execute("DELETE FROM faucet.faucet WHERE id = ?", (faucet_id,))
    await db.execute("DELETE FROM faucet.secret WHERE faucet_id = ?", (faucet_id,))


async def get_faucet(faucet_id: str) -> Optional[Faucet]:
    row = await db.fetchone("SELECT * FROM faucet.faucet WHERE id = ?", (faucet_id,))
    return Faucet(**row) if row else None


async def get_active_faucets() -> list[Faucet]:
    now = int(datetime.datetime.now().timestamp())
    ph = db.timestamp_placeholder
    rows = await db.fetchall(
        f"""
        SELECT * FROM faucet.faucet WHERE start_time <= {ph} AND end_time >= {ph}
        """,
        (
            now,
            now,
        ),
    )
    return [Faucet(**row) for row in rows]


async def get_faucets(wallet_ids: list[str]) -> list[Faucet]:
    rows = await db.fetchall(
        "SELECT * FROM faucet.faucet WHERE wallet IN ({})".format(
            ",".join("?" * len(wallet_ids))
        ),
        (*wallet_ids,),
    )
    return [Faucet(**row) for row in rows]


async def update_faucet(faucet: Faucet) -> Faucet:
    await db.execute(
        update_query("faucet.faucet", faucet),
        (*faucet.dict().values(), faucet.id),
    )
    return faucet


async def create_faucet_secret(secret: FaucetSecret) -> FaucetSecret:
    await db.execute(
        insert_query("faucet.secret", secret),
        (*secret.dict().values(),),
    )
    return secret


async def get_faucet_secret(k1: str) -> Optional[FaucetSecret]:
    row = await db.fetchone("SELECT * FROM faucet.secret WHERE k1 = ?", (k1,))
    return FaucetSecret(**row) if row else None


async def get_next_faucet_secret(faucet_id: str) -> Optional[FaucetSecret]:
    row = await db.fetchone(
        """
        SELECT * FROM faucet.secret
        WHERE used_time IS NULL AND faucet_id = ?
        """,
        (faucet_id,),
    )
    return FaucetSecret(**row) if row else None


async def delete_faucet_secret(k1: str) -> None:
    await db.execute("DELETE FROM faucet.secret WHERE k1 = ?", (k1,))


async def update_faucet_secret(secret: FaucetSecret) -> FaucetSecret:
    await db.execute(
        update_query("faucet.secret", secret, "WHERE k1 = ?"),
        (*secret.dict().values(), secret.k1),
    )
    return secret
