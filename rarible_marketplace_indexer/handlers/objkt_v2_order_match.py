from dipdup.context import HandlerContext
from dipdup.models import Transaction

from rarible_marketplace_indexer.action.objkt_v2_action import ObjktV2MatchAction
from rarible_marketplace_indexer.types.objkt_marketplace_v2.parameter.fulfill_ask import FulfillAskParameter
from rarible_marketplace_indexer.types.objkt_marketplace_v2.storage import ObjktMarketplaceV2Storage


async def objkt_v2_order_match(
    ctx: HandlerContext,
    fulfill_ask: Transaction[FulfillAskParameter, ObjktMarketplaceV2Storage],
) -> None:
    await ObjktV2MatchAction.handle(fulfill_ask, ctx.datasource)
