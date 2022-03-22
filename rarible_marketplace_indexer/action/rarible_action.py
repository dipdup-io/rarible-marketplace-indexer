from dipdup.datasources.tzkt.datasource import TzktDatasource
from dipdup.models import Transaction

from rarible_marketplace_indexer.action.abstract_action import AbstractCancelAction
from rarible_marketplace_indexer.action.abstract_action import AbstractListAction
from rarible_marketplace_indexer.action.abstract_action import AbstractMatchAction
from rarible_marketplace_indexer.action.dto import CancelDto
from rarible_marketplace_indexer.action.dto import ListDto
from rarible_marketplace_indexer.action.dto import MatchDto
from rarible_marketplace_indexer.models import PlatformEnum
from rarible_marketplace_indexer.types.rarible_exchange.parameter.buy import BuyParameter
from rarible_marketplace_indexer.types.rarible_exchange.parameter.cancel_sale import CancelSaleParameter
from rarible_marketplace_indexer.types.rarible_exchange.parameter.sell import SellParameter
from rarible_marketplace_indexer.types.rarible_exchange.storage import RaribleExchangeStorage
from rarible_marketplace_indexer.types.tezos_objects.tezos_currency import AssetValue
from rarible_marketplace_indexer.types.tezos_objects.tezos_currency import Xtz
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import ImplicitAccountAddress
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OriginatedAccountAddress


class RaribleAware:
    @staticmethod
    def get_order_hash(
        contract: OriginatedAccountAddress,
        token_id: int,
        seller: ImplicitAccountAddress,
    ) -> str:
        return str(abs(hash(f'{contract}:{token_id}@{seller}')))


class RaribleListAction(AbstractListAction):
    platform = PlatformEnum.RARIBLE
    RaribleListTransaction = Transaction[SellParameter, RaribleExchangeStorage]

    @staticmethod
    def _get_list_dto(
        transaction: RaribleListTransaction,
        datasource: TzktDatasource,
    ) -> ListDto:
        internal_order_id = RaribleAware.get_order_hash(
            contract=OriginatedAccountAddress(transaction.parameter.s_asset_contract),
            token_id=int(transaction.parameter.s_asset_token_id),
            seller=ImplicitAccountAddress(transaction.parameter.s_seller),
        )

        return ListDto(
            internal_order_id=internal_order_id,
            maker=ImplicitAccountAddress(transaction.parameter.s_seller),
            contract=OriginatedAccountAddress(transaction.parameter.s_asset_contract),
            token_id=int(transaction.parameter.s_asset_token_id),
            amount=AssetValue(transaction.parameter.s_sale.sale_asset_qty),
            object_price=Xtz.from_u_tezos(transaction.parameter.s_sale.sale_amount),
        )


class RaribleCancelAction(AbstractCancelAction):
    platform = PlatformEnum.RARIBLE
    RaribleCancelTransaction = Transaction[CancelSaleParameter, RaribleExchangeStorage]

    @staticmethod
    def _get_cancel_dto(transaction: RaribleCancelTransaction, datasource: TzktDatasource) -> CancelDto:
        internal_order_id = RaribleAware.get_order_hash(
            contract=OriginatedAccountAddress(transaction.parameter.cs_asset_contract),
            token_id=int(transaction.parameter.cs_asset_token_id),
            seller=ImplicitAccountAddress(transaction.parameter.cs_seller),
        )

        return CancelDto(internal_order_id=internal_order_id)


class RaribleMatchAction(AbstractMatchAction):
    platform = PlatformEnum.RARIBLE
    RaribleMatchTransaction = Transaction[BuyParameter, RaribleExchangeStorage]

    @staticmethod
    def _get_match_dto(transaction: RaribleMatchTransaction, datasource: TzktDatasource) -> MatchDto:
        internal_order_id = RaribleAware.get_order_hash(
            contract=OriginatedAccountAddress(transaction.parameter.b_asset_contract),
            token_id=int(transaction.parameter.b_asset_token_id),
            seller=ImplicitAccountAddress(transaction.parameter.b_seller),
        )

        return MatchDto(
            internal_order_id=internal_order_id,
            match_amount=AssetValue(1),
            match_timestamp=transaction.data.timestamp,
        )
