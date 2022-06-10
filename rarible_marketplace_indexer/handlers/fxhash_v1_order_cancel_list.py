from dipdup.context import HandlerContext
from dipdup.models import Transaction

from rarible_marketplace_indexer.event.fxhash_v1_action import FxhashV1OrderCancelEvent
from rarible_marketplace_indexer.types.fxhash_marketplace_v1.parameter.cancel_offer import CancelOfferParameter
from rarible_marketplace_indexer.types.fxhash_marketplace_v1.storage import FxhashMarketplaceV1Storage

async def fxhash_v1_order_cancel_list(
    ctx: HandlerContext,
    cancel_offer: Transaction[CancelOfferParameter, FxhashMarketplaceV1Storage],
) -> None:
    await FxhashV1OrderCancelEvent.handle(cancel_offer, ctx.datasource)
