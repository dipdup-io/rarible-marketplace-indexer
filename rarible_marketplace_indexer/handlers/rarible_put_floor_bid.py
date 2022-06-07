from dipdup.context import HandlerContext
from dipdup.models import Transaction

from rarible_marketplace_indexer.event.rarible_action import RariblePutFloorBidEvent
from rarible_marketplace_indexer.types.rarible_bids.parameter.put_floor_bid import PutFloorBidParameter
from rarible_marketplace_indexer.types.rarible_bids.storage import RaribleBidsStorage


async def rarible_put_floor_bid(
    ctx: HandlerContext,
    floor_bid: Transaction[PutFloorBidParameter, RaribleBidsStorage],
) -> None:
    await RariblePutFloorBidEvent.handle(floor_bid, ctx.datasource)
