from fastapi import Query
from pydantic import BaseModel


class CreateFaucetData(BaseModel):
    wallet: str = Query(...)
    title: str = Query(...)
    description: str = Query(...)
    min_withdrawable: int = Query(..., ge=1)
    max_withdrawable: int = Query(..., ge=1)
    min_wait_time: int = Query(..., ge=1)
    max_wait_time: int = Query(..., ge=1)
    start_time: int = Query(..., ge=1)
    end_time: int = Query(..., ge=1)


class FaucetLink(BaseModel):
    id: str
    wallet: str
    title: str
    description: str
    min_withdrawable: int
    max_withdrawable: int
    min_wait_time: int
    max_wait_time: int
    start_time: int
    end_time: int
# from lnurl import LnurlWithdrawResponse
# from lnurl.types import ClearnetUrl, MilliSatoshi
    # def lnurl_response(self, url: str, k1: str) -> LnurlWithdrawResponse:
    #     # url = req.url_for("withdraw.api_lnurl_callback")
    #     url = ClearnetUrl(url)
    #     return LnurlWithdrawResponse(
    #         callback=ClearnetUrl(url),
    #         k1=self.k1,
    #         minWithdrawable=MilliSatoshi(self.min_withdrawable * 1000),
    #         maxWithdrawable=MilliSatoshi(self.max_withdrawable * 1000),
    #         defaultDescription=self.title,
    #     )


class FaucetWithdraw(BaseModel):
    id: str
    link_id: str
    amount: int
    start_time: int
    end_time: int
    spent: bool = False
    spent_time: int = 0
