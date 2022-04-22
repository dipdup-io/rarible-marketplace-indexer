from dipdup.datasources.tzkt.datasource import TzktDatasource
from dipdup.models import Transaction

from rarible_marketplace_indexer.event.abstract_action import AbstractOrderCancelEvent
from rarible_marketplace_indexer.event.abstract_action import AbstractOrderListEvent
from rarible_marketplace_indexer.event.abstract_action import AbstractOrderMatchEvent
from rarible_marketplace_indexer.event.dto import CancelDto
from rarible_marketplace_indexer.event.dto import ListDto
from rarible_marketplace_indexer.event.dto import MatchDto
from rarible_marketplace_indexer.models import PlatformEnum
from rarible_marketplace_indexer.types.objkt_marketplace.parameter.ask import AskParameter
from rarible_marketplace_indexer.types.objkt_marketplace.parameter.fulfill_ask import FulfillAskParameter
from rarible_marketplace_indexer.types.objkt_marketplace.parameter.retract_ask import RetractAskParameter
from rarible_marketplace_indexer.types.objkt_marketplace.storage import ObjktMarketplaceStorage
from rarible_marketplace_indexer.types.tezos_objects.asset_value.asset_value import AssetValue
from rarible_marketplace_indexer.types.tezos_objects.asset_value.xtz_value import Xtz
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import ImplicitAccountAddress
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OriginatedAccountAddress


class ObjktOrderListEvent(AbstractOrderListEvent):
    platform = PlatformEnum.OBJKT
    ObjktListTransaction = Transaction[AskParameter, ObjktMarketplaceStorage]

    @staticmethod
    def _get_list_dto(
        transaction: ObjktListTransaction,
        datasource: TzktDatasource,
    ) -> ListDto:
        return ListDto(
            internal_order_id=str(int(transaction.storage.ask_id) - 1),
            maker=ImplicitAccountAddress(transaction.data.sender_address),
            contract=OriginatedAccountAddress(transaction.parameter.fa2),
            token_id=int(transaction.parameter.objkt_id),
            amount=AssetValue(transaction.parameter.amount),
            object_price=Xtz.from_u_tezos(transaction.parameter.price),
        )


class ObjktOrderCancelEvent(AbstractOrderCancelEvent):
    platform = PlatformEnum.OBJKT
    ObjktCancelTransaction = Transaction[RetractAskParameter, ObjktMarketplaceStorage]

    @staticmethod
    def _get_cancel_dto(transaction: ObjktCancelTransaction, datasource: TzktDatasource) -> CancelDto:
        return CancelDto(internal_order_id=transaction.parameter.__root__)


class ObjktOrderMatchEvent(AbstractOrderMatchEvent):
    platform = PlatformEnum.OBJKT
    ObjktMatchTransaction = Transaction[FulfillAskParameter, ObjktMarketplaceStorage]

    @staticmethod
    def _get_match_dto(transaction: ObjktMatchTransaction, datasource: TzktDatasource) -> MatchDto:
        return MatchDto(
            internal_order_id=transaction.parameter.__root__,
            match_amount=AssetValue(1),
            match_timestamp=transaction.data.timestamp,
        )
