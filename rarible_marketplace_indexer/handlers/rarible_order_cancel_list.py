from dipdup.context import HandlerContext
from dipdup.models import Transaction

from rarible_marketplace_indexer.event.rarible_action import RaribleOrderCancelEvent
from rarible_marketplace_indexer.types.rarible_exchange.parameter.cancel_sale import CancelSaleParameter
from rarible_marketplace_indexer.types.rarible_exchange.storage import RaribleExchangeStorage


async def rarible_order_cancel_list(
    ctx: HandlerContext,
    cancel_sale: Transaction[CancelSaleParameter, RaribleExchangeStorage],
) -> None:
    await RaribleOrderCancelEvent.handle(cancel_sale, ctx.datasource)
