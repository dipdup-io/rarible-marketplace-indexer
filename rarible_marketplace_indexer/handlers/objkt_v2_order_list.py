from dipdup.context import HandlerContext
from dipdup.models import Transaction

from rarible_marketplace_indexer.event.objkt_v2_action import ObjktV2OrderListEvent
from rarible_marketplace_indexer.types.objkt_marketplace_v2.parameter.ask import AskParameter
from rarible_marketplace_indexer.types.objkt_marketplace_v2.storage import ObjktMarketplaceV2Storage


async def objkt_v2_order_list(
    ctx: HandlerContext,
    ask: Transaction[AskParameter, ObjktMarketplaceV2Storage],
) -> None:
    await ObjktV2OrderListEvent.handle(ask, ctx.datasource)
