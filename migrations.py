async def m002_initial(db):
    await db.execute(
        """
        CREATE TABLE faucet.faucet (
            id TEXT PRIMARY KEY,
            wallet TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP NOT NULL,
            interval INTEGER NOT NULL
        );
    """
    )
    await db.execute(
        """
        CREATE TABLE faucet.faucet_secrets (
            k1 TEXT PRIMARY KEY,
            faucet_id TEXT NOT NULL,
            used_time TIMESTAMP
        );
    """
    )
