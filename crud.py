from datetime import datetime
from typing import List, Optional, Tuple

from lnbits.db import Database
from lnbits.helpers import urlsafe_short_hash

from .models import CreateFaucetData, FaucetLink

db = Database("ext_faucet")


async def create_faucet_link(
    data: CreateFaucetData, wallet_id: str
) -> FaucetLink:
    link_id = urlsafe_short_hash()#[:22]
    await db.execute(
        """
        INSERT INTO faucet.faucet_link (
            id,
            wallet,
            title,
            min_faucetable,
            max_faucetable,
            uses,
            wait_time,
            is_unique,
            unique_hash,
            k1,
            open_time,
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            link_id,
            wallet_id,
            data.title,
            data.min_faucetable,
            data.max_faucetable,
            data.uses,
            data.wait_time,
            int(data.is_unique),
            urlsafe_short_hash(),
            urlsafe_short_hash(),
            int(datetime.now().timestamp()) + data.wait_time,
        ),
    )
    link = await get_faucet_link(link_id, 0)
    assert link, "Newly created link couldn't be retrieved"
    return link


async def get_faucet_link(link_id: str, num=0) -> Optional[FaucetLink]:
    row = await db.fetchone(
        "SELECT * FROM faucet.faucet_link WHERE id = ?", (link_id,)
    )
    if not row:
        return None

    link = dict(**row)
    link["number"] = num

    return FaucetLink.parse_obj(link)


async def get_faucet_links(
    wallet_ids: List[str], limit: int, offset: int
) -> Tuple[List[FaucetLink], int]:
    rows = await db.fetchall(
        """
        SELECT * FROM faucet.faucet_link
        WHERE wallet IN ({})
        ORDER BY open_time DESC
        LIMIT ? OFFSET ?
        """.format(
            ",".join("?" * len(wallet_ids))
        ),
        (*wallet_ids, limit, offset),
    )

    total = await db.fetchone(
        """
        SELECT COUNT(*) as total FROM faucet.faucet_link
        WHERE wallet IN ({})
        """.format(
            ",".join("?" * len(wallet_ids))
        ),
        (*wallet_ids,),
    )

    return [FaucetLink(**row) for row in rows], total["total"]


async def update_faucet_link(link_id: str, **kwargs) -> Optional[FaucetLink]:
    q = ", ".join([f"{field[0]} = ?" for field in kwargs.items()])
    await db.execute(
        f"UPDATE faucet.faucet_link SET {q} WHERE id = ?",
        (*kwargs.values(), link_id),
    )
    row = await db.fetchone(
        "SELECT * FROM faucet.faucet_link WHERE id = ?", (link_id,)
    )
    return FaucetLink(**row) if row else None


async def delete_faucet_link(link_id: str) -> None:
    await db.execute("DELETE FROM faucet.faucet_link WHERE id = ?", (link_id,))
