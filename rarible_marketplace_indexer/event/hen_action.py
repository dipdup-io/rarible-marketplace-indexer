from dipdup.datasources.tzkt.datasource import TzktDatasource
from dipdup.models import Transaction

from rarible_marketplace_indexer.event.abstract_action import AbstractOrderCancelEvent
from rarible_marketplace_indexer.event.abstract_action import AbstractOrderListEvent
from rarible_marketplace_indexer.event.abstract_action import AbstractOrderMatchEvent
from rarible_marketplace_indexer.event.dto import CancelDto
from rarible_marketplace_indexer.event.dto import ListDto
from rarible_marketplace_indexer.event.dto import MakeDto
from rarible_marketplace_indexer.event.dto import MatchDto
from rarible_marketplace_indexer.event.dto import TakeDto
from rarible_marketplace_indexer.models import PlatformEnum
from rarible_marketplace_indexer.types.hen_marketplace.parameter.cancel_swap import CancelSwapParameter
from rarible_marketplace_indexer.types.hen_marketplace.parameter.collect import CollectParameter
from rarible_marketplace_indexer.types.hen_marketplace.parameter.swap import SwapParameter
from rarible_marketplace_indexer.types.hen_marketplace.storage import HenMarketplaceStorage
from rarible_marketplace_indexer.types.rarible_api_objects.asset.enum import AssetClassEnum
from rarible_marketplace_indexer.types.tezos_objects.asset_value.asset_value import AssetValue
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import ImplicitAccountAddress
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OriginatedAccountAddress


class HENOrderListEvent(AbstractOrderListEvent):
    platform = PlatformEnum.HEN
    HENListTransaction = Transaction[SwapParameter, HenMarketplaceStorage]

    @staticmethod
    def _get_list_dto(
        transaction: HENListTransaction,
        datasource: TzktDatasource,
    ) -> ListDto:
        make_value = AssetValue(transaction.parameter.objkt_amount)
        take_value = AssetValue(transaction.parameter.xtz_per_objkt)

        return ListDto(
            internal_order_id=str(int(transaction.storage.counter) - 1),
            maker=ImplicitAccountAddress(transaction.data.sender_address),
            make=MakeDto(
                asset_class=AssetClassEnum.MULTI_TOKEN,
                contract=OriginatedAccountAddress(transaction.storage.objkt),
                token_id=int(transaction.parameter.objkt_id),
                value=make_value,
            ),
            take=TakeDto(
                asset_class=AssetClassEnum.XTZ,
                contract=None,
                token_id=None,
                value=take_value,
            ),
        )


class HENOrderCancelEvent(AbstractOrderCancelEvent):
    platform = PlatformEnum.HEN
    HENCancelTransaction = Transaction[CancelSwapParameter, HenMarketplaceStorage]

    @staticmethod
    def _get_cancel_dto(transaction: HENCancelTransaction, datasource: TzktDatasource) -> CancelDto:
        return CancelDto(
            internal_order_id=transaction.parameter.__root__,
        )


class HENOrderMatchEvent(AbstractOrderMatchEvent):
    platform = PlatformEnum.HEN
    HENMatchTransaction = Transaction[CollectParameter, HenMarketplaceStorage]

    @staticmethod
    def _get_match_dto(transaction: HENMatchTransaction, datasource: TzktDatasource) -> MatchDto:
        return MatchDto(
            internal_order_id=transaction.parameter.__root__,
            match_amount=AssetValue(1),
            match_timestamp=transaction.data.timestamp,
        )
