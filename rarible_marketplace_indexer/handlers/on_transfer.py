from dipdup.context import HandlerContext
from dipdup.models import TokenTransferData

from rarible_marketplace_indexer.producer.helper import producer_send
from rarible_marketplace_indexer.types.rarible_api_objects.activity.token.factory import RaribleApiTokenActivityFactory


async def on_transfer(
    ctx: HandlerContext,
    token_transfer: TokenTransferData,
) -> None:
    token_transfer_activity = RaribleApiTokenActivityFactory.build(token_transfer, ctx.datasource)
    await producer_send(token_transfer_activity)
