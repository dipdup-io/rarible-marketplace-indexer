from dipdup.context import HandlerContext
from dipdup.models import Transaction

from rarible_marketplace_indexer.event.fxhash_v1_action import FxhashV1OrderMatchEvent
from rarible_marketplace_indexer.types.fxhash_marketplace_v1.storage import FxhashMarketplaceV1Storage
from rarible_marketplace_indexer.types.fxhash_marketplace_v1.parameter.collect import CollectParameter

async def fxhash_v1_order_match(
    ctx: HandlerContext,
    collect: Transaction[CollectParameter, FxhashMarketplaceV1Storage],
) -> None:
    await FxhashV1OrderMatchEvent.handle(collect, ctx.datasource)
