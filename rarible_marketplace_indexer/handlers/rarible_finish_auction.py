from dipdup.context import HandlerContext
from dipdup.models import Transaction

from rarible_marketplace_indexer.event.rarible_action import RaribleFinishAuctionEvent
from rarible_marketplace_indexer.types.rarible_auctions.parameter.finish_auction import FinishAuctionParameter
from rarible_marketplace_indexer.types.rarible_auctions.storage import RaribleAuctionsStorage


async def rarible_finish_auction(
    ctx: HandlerContext,
    finish_auction: Transaction[FinishAuctionParameter, RaribleAuctionsStorage],
) -> None:
    await RaribleFinishAuctionEvent.handle(finish_auction, ctx.datasource)
