
from rarible_marketplace_indexer.types.rarible_auctions.storage import RaribleAuctionsStorage
from dipdup.context import HandlerContext
from rarible_marketplace_indexer.types.rarible_auctions.parameter.finish_auction import FinishAuctionParameter
from dipdup.models import Transaction

async def rarible_finish_auction(
    ctx: HandlerContext,
    finish_auction: Transaction[FinishAuctionParameter, RaribleAuctionsStorage],
) -> None:
    ...