from datetime import datetime
from typing import Optional

from pydantic.dataclasses import dataclass


@dataclass
class ListDto:
    internal_order_id: int
    maker: str
    contract: str
    token_id: str
    amount: str
    object_price: str
    started_at: Optional[datetime] = None  # for marketplaces with the possibility of a delayed start of sales


@dataclass
class CancelDto:
    internal_order_id: int
