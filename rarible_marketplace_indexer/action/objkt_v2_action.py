from dipdup.datasources.tzkt.datasource import TzktDatasource
from dipdup.models import Transaction

from rarible_marketplace_indexer.action.abstract_action import AbstractCancelAction
from rarible_marketplace_indexer.action.abstract_action import AbstractListAction
from rarible_marketplace_indexer.action.abstract_action import AbstractMatchAction
from rarible_marketplace_indexer.action.dto import CancelDto
from rarible_marketplace_indexer.action.dto import ListDto
from rarible_marketplace_indexer.action.dto import MatchDto
from rarible_marketplace_indexer.models import PlatformEnum
from rarible_marketplace_indexer.types.objkt_marketplace_v2.parameter.ask import AskParameter
from rarible_marketplace_indexer.types.objkt_marketplace_v2.parameter.fulfill_ask import FulfillAskParameter
from rarible_marketplace_indexer.types.objkt_marketplace_v2.parameter.retract_ask import RetractAskParameter
from rarible_marketplace_indexer.types.objkt_marketplace_v2.storage import ObjktMarketplaceV2Storage
from rarible_marketplace_indexer.types.tezos_objects.asset_value.asset_value import AssetValue
from rarible_marketplace_indexer.types.tezos_objects.asset_value.xtz_value import Xtz
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import ImplicitAccountAddress
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OriginatedAccountAddress


class ObjktV2ListAction(AbstractListAction):
    platform = PlatformEnum.OBJKT_V2
    ObjktListTransaction = Transaction[AskParameter, ObjktMarketplaceV2Storage]

    @staticmethod
    def _get_list_dto(
        transaction: ObjktListTransaction,
        datasource: TzktDatasource,
    ) -> ListDto:
        return ListDto(
            internal_order_id=str(int(transaction.storage.next_ask_id) - 1),
            maker=ImplicitAccountAddress(transaction.data.sender_address),
            contract=OriginatedAccountAddress(transaction.parameter.token.address),
            token_id=int(transaction.parameter.token.token_id),
            amount=AssetValue(transaction.parameter.editions),
            object_price=Xtz.from_u_tezos(transaction.parameter.amount),
        )


class ObjktV2CancelAction(AbstractCancelAction):
    platform = PlatformEnum.OBJKT_V2
    ObjktCancelTransaction = Transaction[RetractAskParameter, ObjktMarketplaceV2Storage]

    @staticmethod
    def _get_cancel_dto(transaction: ObjktCancelTransaction, datasource: TzktDatasource) -> CancelDto:
        return CancelDto(internal_order_id=transaction.parameter.__root__)


class ObjktV2MatchAction(AbstractMatchAction):
    platform = PlatformEnum.OBJKT_V2
    ObjktMatchTransaction = Transaction[FulfillAskParameter, ObjktMarketplaceV2Storage]

    @staticmethod
    def _get_match_dto(transaction: ObjktMatchTransaction, datasource: TzktDatasource) -> MatchDto:
        return MatchDto(
            internal_order_id=transaction.parameter.ask_id,
            match_amount=AssetValue(1),
            match_timestamp=transaction.data.timestamp,
        )
