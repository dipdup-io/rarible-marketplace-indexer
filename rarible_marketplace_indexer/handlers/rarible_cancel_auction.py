
from rarible_marketplace_indexer.types.rarible_auctions.storage import RaribleAuctionsStorage
from rarible_marketplace_indexer.types.rarible_auctions.parameter.cancel_auction import CancelAuctionParameter
from dipdup.context import HandlerContext
from dipdup.models import Transaction

async def rarible_cancel_auction(
    ctx: HandlerContext,
    cancel_auction: Transaction[CancelAuctionParameter, RaribleAuctionsStorage],
) -> None:
    ...