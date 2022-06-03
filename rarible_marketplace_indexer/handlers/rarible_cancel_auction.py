from dipdup.context import HandlerContext
from dipdup.models import Transaction

from rarible_marketplace_indexer.event.rarible_action import RaribleCancelAuctionEvent
from rarible_marketplace_indexer.types.rarible_auctions.parameter.cancel_auction import CancelAuctionParameter
from rarible_marketplace_indexer.types.rarible_auctions.storage import RaribleAuctionsStorage


async def rarible_cancel_auction(
    ctx: HandlerContext,
    cancel_auction: Transaction[CancelAuctionParameter, RaribleAuctionsStorage],
) -> None:
    await RaribleCancelAuctionEvent.handle(cancel_auction, ctx.datasource)
