from dipdup.context import HandlerContext
from dipdup.models import Transaction

from rarible_marketplace_indexer.event.rarible_action import RaribleFloorBidCancelEvent
from rarible_marketplace_indexer.types.rarible_bids.parameter.cancel_floor_bid import CancelFloorBidParameter
from rarible_marketplace_indexer.types.rarible_bids.storage import RaribleBidsStorage


async def rarible_cancel_floor_bid(
    ctx: HandlerContext,
    cancel_bid: Transaction[CancelFloorBidParameter, RaribleBidsStorage],
) -> None:
    await RaribleFloorBidCancelEvent.handle(cancel_bid, ctx.datasource)
