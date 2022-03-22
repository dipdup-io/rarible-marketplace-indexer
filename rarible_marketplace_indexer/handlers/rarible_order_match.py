from dipdup.context import HandlerContext
from dipdup.models import Transaction

from rarible_marketplace_indexer.action.rarible_action import RaribleMatchAction
from rarible_marketplace_indexer.types.rarible_exchange.parameter.buy import BuyParameter
from rarible_marketplace_indexer.types.rarible_exchange.storage import RaribleExchangeStorage


async def rarible_order_match(
    ctx: HandlerContext,
    buy: Transaction[BuyParameter, RaribleExchangeStorage],
) -> None:
    await RaribleMatchAction.handle(buy, ctx.datasource)
