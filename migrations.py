async def m005_initial(db):
    await db.execute(
        """
        CREATE TABLE faucet.faucet (
            id TEXT PRIMARY KEY,
            wallet TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP NOT NULL,
            next_tick TIMESTAMP NOT NULL,
            interval INTEGER NOT NULL,
            current_k1 TEXT,
            lnurl TEXT,
            uses INTEGER NOT NULL,
            current_use INTEGER NOT NULL
        );
    """
    )
    await db.execute(
        """
        CREATE TABLE faucet.secret (
            k1 TEXT PRIMARY KEY,
            faucet_id TEXT NOT NULL,
            used_time TIMESTAMP
        );
    """
    )
