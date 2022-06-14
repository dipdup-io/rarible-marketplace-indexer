from dipdup.context import HandlerContext
from dipdup.models import Transaction

from rarible_marketplace_indexer.event.rarible_action import RaribleAcceptBidEvent
from rarible_marketplace_indexer.types.rarible_bids.parameter.accept_bid import AcceptBidParameter
from rarible_marketplace_indexer.types.rarible_bids.storage import RaribleBidsStorage


async def rarible_accept_bid(
    ctx: HandlerContext,
    sell: Transaction[AcceptBidParameter, RaribleBidsStorage],
) -> None:
    await RaribleAcceptBidEvent.handle(sell, ctx.datasource)
