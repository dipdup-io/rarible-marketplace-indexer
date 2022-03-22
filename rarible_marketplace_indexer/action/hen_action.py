from dipdup.datasources.tzkt.datasource import TzktDatasource
from dipdup.models import Transaction

from rarible_marketplace_indexer.action.abstract_action import AbstractCancelAction
from rarible_marketplace_indexer.action.abstract_action import AbstractListAction
from rarible_marketplace_indexer.action.abstract_action import AbstractMatchAction
from rarible_marketplace_indexer.action.abstract_action import MatchDto
from rarible_marketplace_indexer.action.dto import CancelDto
from rarible_marketplace_indexer.action.dto import ListDto
from rarible_marketplace_indexer.models import PlatformEnum
from rarible_marketplace_indexer.types.hen_marketplace.parameter.cancel_swap import CancelSwapParameter
from rarible_marketplace_indexer.types.hen_marketplace.parameter.collect import CollectParameter
from rarible_marketplace_indexer.types.hen_marketplace.parameter.swap import SwapParameter
from rarible_marketplace_indexer.types.hen_marketplace.storage import HenMarketplaceStorage


class HENListAction(AbstractListAction):
    platform = PlatformEnum.HEN
    HENListTransaction = Transaction[SwapParameter, HenMarketplaceStorage]

    @staticmethod
    def _get_list_dto(
        transaction: HENListTransaction,
        datasource: TzktDatasource,
    ) -> ListDto:
        return ListDto(
            internal_order_id=int(transaction.storage.counter) - 1,
            maker=transaction.data.sender_address,
            contract=transaction.storage.objkt,
            token_id=transaction.parameter.objkt_id,
            amount=transaction.parameter.objkt_amount,
            object_price=transaction.parameter.xtz_per_objkt,
        )


class HENCancelAction(AbstractCancelAction):
    platform = PlatformEnum.HEN
    HENCancelTransaction = Transaction[CancelSwapParameter, HenMarketplaceStorage]

    @staticmethod
    def _get_cancel_dto(transaction: HENCancelTransaction, datasource: TzktDatasource) -> CancelDto:
        return CancelDto(
            internal_order_id=int(transaction.parameter.__root__),
        )


class HENMatchAction(AbstractMatchAction):
    platform = PlatformEnum.HEN
    HENMatchTransaction = Transaction[CollectParameter, HenMarketplaceStorage]

    @staticmethod
    def _get_match_dto(transaction: HENMatchTransaction, datasource: TzktDatasource) -> MatchDto:
        pass
