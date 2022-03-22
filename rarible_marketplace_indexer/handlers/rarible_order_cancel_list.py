from dipdup.context import HandlerContext
from dipdup.models import Transaction

from rarible_marketplace_indexer.action.rarible_action import RaribleCancelAction
from rarible_marketplace_indexer.types.rarible_exchange.parameter.cancel_sale import CancelSaleParameter
from rarible_marketplace_indexer.types.rarible_exchange.storage import RaribleExchangeStorage


async def rarible_order_cancel_list(
    ctx: HandlerContext,
    cancel_sale: Transaction[CancelSaleParameter, RaribleExchangeStorage],
) -> None:
    await RaribleCancelAction.handle(cancel_sale, ctx.datasource)
