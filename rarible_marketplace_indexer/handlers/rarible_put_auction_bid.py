from dipdup.context import HandlerContext
from dipdup.models import Transaction

from rarible_marketplace_indexer.event.rarible_action import RariblePutAuctionBidEvent
from rarible_marketplace_indexer.types.rarible_auctions.parameter.put_bid import PutBidParameter
from rarible_marketplace_indexer.types.rarible_auctions.storage import RaribleAuctionsStorage


async def rarible_put_auction_bid(
    ctx: HandlerContext,
    put_auction_bid: Transaction[PutBidParameter, RaribleAuctionsStorage],
) -> None:
    await RariblePutAuctionBidEvent.handle(put_auction_bid, ctx.datasource)
