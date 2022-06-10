from dipdup.context import HandlerContext
from dipdup.models import Transaction

from rarible_marketplace_indexer.event.fxhash_v1_action import FxhashV1OrderListEvent
from rarible_marketplace_indexer.types.fxhash_marketplace_v1.parameter.offer import OfferParameter
from rarible_marketplace_indexer.types.fxhash_marketplace_v1.storage import FxhashMarketplaceV1Storage

async def fxhash_v1_order_list(
    ctx: HandlerContext,
    offer: Transaction[OfferParameter, FxhashMarketplaceV1Storage],
) -> None:
    await FxhashV1OrderListEvent.handle(offer, ctx.datasource)
