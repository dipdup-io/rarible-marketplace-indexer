from dipdup.context import HandlerContext
from dipdup.models import Transaction

from rarible_marketplace_indexer.action.hen_action import HENListAction
from rarible_marketplace_indexer.types.hen_marketplace.parameter.swap import SwapParameter
from rarible_marketplace_indexer.types.hen_marketplace.storage import HenMarketplaceStorage


async def hen_order_list(
    ctx: HandlerContext,
    swap: Transaction[SwapParameter, HenMarketplaceStorage],
) -> None:
    await HENListAction.handle(swap, ctx.datasource)
