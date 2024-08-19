import datetime
from typing import Optional

from fastapi import Query
from pydantic import BaseModel


class CreateFaucet(BaseModel):
    wallet: str = Query(...)
    title: str = Query(...)
    description: str = Query(...)
    interval: int = Query(..., gt=0)
    start_time: datetime.datetime = Query(...)
    end_time: datetime.datetime = Query(...)


class Faucet(BaseModel):
    id: str
    wallet: str
    title: str
    description: str
    interval: int
    start_time: datetime.datetime
    end_time: datetime.datetime
    next_tick: datetime.datetime
    uses: int
    current_use: int = 0
    current_k1: Optional[str] = None


class FaucetSecret(BaseModel):
    k1: str
    faucet_id: str
    used_time: Optional[datetime.datetime] = None
