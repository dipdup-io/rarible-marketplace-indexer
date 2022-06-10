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
from rarible_marketplace_indexer.types.fxhash_marketplace_v1.parameter.offer import OfferParameter
from rarible_marketplace_indexer.types.fxhash_marketplace_v1.parameter.cancel_offer import CancelOfferParameter
from rarible_marketplace_indexer.types.fxhash_marketplace_v1.parameter.collect import CollectParameter
from rarible_marketplace_indexer.types.fxhash_marketplace_v1.storage import FxhashMarketplaceV1Storage
from rarible_marketplace_indexer.types.rarible_api_objects.asset.enum import AssetClassEnum
from rarible_marketplace_indexer.types.tezos_objects.asset_value.asset_value import AssetValue
from rarible_marketplace_indexer.types.tezos_objects.asset_value.xtz_value import Xtz
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import ImplicitAccountAddress
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OriginatedAccountAddress


class FxhashV1OrderListEvent(AbstractOrderListEvent):
    platform = PlatformEnum.FXHASH_V1
    FxhashListTransaction = Transaction[OfferParameter, FxhashMarketplaceV1Storage]

    @staticmethod
    def _get_list_dto(
        transaction: FxhashListTransaction,
        datasource: TzktDatasource,
    ) -> ListDto:
        make_value = AssetValue(1)
        make_price = Xtz.from_u_tezos(transaction.parameter.price)

        return ListDto(
            internal_order_id=str(int(transaction.storage.counter) - 1),
            maker=ImplicitAccountAddress(transaction.data.sender_address),
            make_price=make_price,
            make=MakeDto(
                asset_class=AssetClassEnum.MULTI_TOKEN,
                contract=OriginatedAccountAddress(transaction.storage.objkts),
                token_id=int(transaction.parameter.objkt_id),
                value=make_value,
            ),
            take=TakeDto(
                asset_class=AssetClassEnum.XTZ,
                contract=None,
                token_id=None,
                value=Xtz(make_value * make_price),
            ),
        )


class FxhashV1OrderCancelEvent(AbstractOrderCancelEvent):
    platform = PlatformEnum.FXHASH_V1
    FxhashCancelTransaction = Transaction[CancelOfferParameter, FxhashMarketplaceV1Storage]

    @staticmethod
    def _get_cancel_dto(transaction: FxhashCancelTransaction, datasource: TzktDatasource) -> CancelDto:
        return CancelDto(internal_order_id=transaction.parameter.__root__)


class FxhashV1OrderMatchEvent(AbstractOrderMatchEvent):
    platform = PlatformEnum.FXHASH_V1
    FxhashMatchTransaction = Transaction[CollectParameter, FxhashMarketplaceV1Storage]

    @staticmethod
    def _get_match_dto(transaction: FxhashMatchTransaction, datasource: TzktDatasource) -> MatchDto:
        return MatchDto(
            internal_order_id=transaction.parameter.__root__,
            match_amount=AssetValue(1),
            match_timestamp=transaction.data.timestamp,
        )
