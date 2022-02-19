from dipdup.context import HandlerContext
from dipdup.models import Transaction

from rarible_marketplace_indexer.types.objkt_marketplace.parameter.ask import AskParameter
from rarible_marketplace_indexer.types.objkt_marketplace.storage import ObjktMarketplaceStorage


async def objkt_order_list(
    ctx: HandlerContext,
    ask: Transaction[AskParameter, ObjktMarketplaceStorage],
) -> None:
    ...
