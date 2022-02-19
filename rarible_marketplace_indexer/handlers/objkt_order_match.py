from dipdup.context import HandlerContext
from dipdup.models import Transaction

from rarible_marketplace_indexer.types.objkt_marketplace.parameter.fulfill_ask import FulfillAskParameter
from rarible_marketplace_indexer.types.objkt_marketplace.storage import ObjktMarketplaceStorage


async def objkt_order_match(
    ctx: HandlerContext,
    fulfill_ask: Transaction[FulfillAskParameter, ObjktMarketplaceStorage],
) -> None:
    ...
