from dipdup.context import HandlerContext
from dipdup.models import Transaction

from rarible_marketplace_indexer.action.objkt_v2_action import ObjktV2CancelAction
from rarible_marketplace_indexer.types.objkt_marketplace_v2.parameter.retract_ask import RetractAskParameter
from rarible_marketplace_indexer.types.objkt_marketplace_v2.storage import ObjktMarketplaceV2Storage


async def objkt_v2_order_cancel_list(
    ctx: HandlerContext,
    retract_ask: Transaction[RetractAskParameter, ObjktMarketplaceV2Storage],
) -> None:
    await ObjktV2CancelAction.handle(retract_ask, ctx.datasource)
