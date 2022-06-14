from dipdup.context import HandlerContext
from dipdup.models import Transaction

from rarible_marketplace_indexer.event.rarible_action import RaribleBidCancelEvent
from rarible_marketplace_indexer.types.rarible_bids.parameter.cancel_bid import CancelBidParameter
from rarible_marketplace_indexer.types.rarible_bids.storage import RaribleBidsStorage


async def rarible_cancel_bid(
    ctx: HandlerContext,
    cancel_bid: Transaction[CancelBidParameter, RaribleBidsStorage],
) -> None:
    await RaribleBidCancelEvent.handle(cancel_bid, ctx.datasource)
