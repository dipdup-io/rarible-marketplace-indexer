from dipdup.context import HookContext

from rarible_marketplace_indexer.producer.container import ProducerContainer


async def on_restart(
    ctx: HookContext,
) -> None:
    await ctx.execute_sql('on_restart')

    ProducerContainer.create_instance(ctx.config.custom, ctx.logger)
    await ProducerContainer.get_instance().start()
