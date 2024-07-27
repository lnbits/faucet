async def m001_initial(db):
    await db.execute(
        """
        CREATE TABLE faucet.faucet_links (
            id TEXT PRIMARY KEY,
            wallet TEXT,
            title TEXT,
            description TEXT,
            min_withdrawable INTEGER,
            max_withdrawable INTEGER,
            min_wait_time INTEGER,
            max_wait_time INTEGER,
            start_time INTEGER,
            end_time INTEGER
        );
    """
    )
    await db.execute(
        """
        CREATE TABLE faucet.faucet_withdraws (
            id TEXT PRIMARY KEY,
            link_id TEXT,
            amount INTEGER,
            time INTEGER,
            spent BOOLEAN DEFAULT 0,
            spent_time INTEGER
        );
    """
    )
