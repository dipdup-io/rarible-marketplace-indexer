# generated by datamodel-codegen:
#   filename:  sell.json

from __future__ import annotations

from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Extra


class SalePayout(BaseModel):
    class Config:
        extra = Extra.forbid

    part_account: str
    part_value: str


class SaleOriginFee(BaseModel):
    class Config:
        extra = Extra.forbid

    part_account: str
    part_value: str


class SSale(BaseModel):
    class Config:
        extra = Extra.forbid

    sale_payouts: List[SalePayout]
    sale_origin_fees: List[SaleOriginFee]
    sale_amount: str
    sale_asset_qty: str
    sale_data_type: Optional[str]
    sale_data: Optional[str]


class SellParameter(BaseModel):
    class Config:
        extra = Extra.forbid

    s_asset_contract: str
    s_asset_token_id: str
    s_seller: str
    s_sale_type: str
    s_sale_asset: str
    s_sale: SSale