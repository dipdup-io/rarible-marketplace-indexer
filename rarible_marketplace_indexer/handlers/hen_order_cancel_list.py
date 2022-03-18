from typing import TYPE_CHECKING

# if TYPE_CHECKING:
from dipdup.context import HandlerContext
from dipdup.models import Transaction

from rarible_marketplace_indexer.action.hen_action import HENCancelAction
from rarible_marketplace_indexer.types.hen_marketplace.parameter.cancel_swap import CancelSwapParameter
from rarible_marketplace_indexer.types.hen_marketplace.storage import HenMarketplaceStorage


async def hen_order_cancel_list(
    ctx: HandlerContext,
    cancel_swap: Transaction[CancelSwapParameter, HenMarketplaceStorage],
) -> None:
    await HENCancelAction.handle(cancel_swap, ctx.datasource)
