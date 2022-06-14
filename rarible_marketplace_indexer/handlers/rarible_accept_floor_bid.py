from dipdup.context import HandlerContext
from dipdup.models import Transaction

from rarible_marketplace_indexer.event.rarible_action import RaribleAcceptFloorBidEvent
from rarible_marketplace_indexer.types.rarible_bids.parameter.accept_floor_bid import AcceptFloorBidParameter
from rarible_marketplace_indexer.types.rarible_bids.storage import RaribleBidsStorage


async def rarible_accept_floor_bid(
    ctx: HandlerContext,
    sell: Transaction[AcceptFloorBidParameter, RaribleBidsStorage],
) -> None:
    await RaribleAcceptFloorBidEvent.handle(sell, ctx.datasource)
