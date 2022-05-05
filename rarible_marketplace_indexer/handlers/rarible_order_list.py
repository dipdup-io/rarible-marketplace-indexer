from dipdup.context import HandlerContext
from dipdup.models import Transaction

from rarible_marketplace_indexer.event.rarible_action import RaribleOrderListEvent
from rarible_marketplace_indexer.types.rarible_exchange.parameter.sell import SellParameter
from rarible_marketplace_indexer.types.rarible_exchange.storage import RaribleExchangeStorage


async def rarible_order_list(
    ctx: HandlerContext,
    sell: Transaction[SellParameter, RaribleExchangeStorage],
) -> None:
    await RaribleOrderListEvent.handle(sell, ctx.datasource)
