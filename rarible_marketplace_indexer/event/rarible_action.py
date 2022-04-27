import uuid
from typing import Callable
from typing import Dict
from typing import Optional
from uuid import uuid5

from base58 import b58encode_check
from dipdup.datasources.tzkt.datasource import TzktDatasource
from dipdup.models import Transaction

from rarible_marketplace_indexer.event.abstract_action import AbstractOrderCancelEvent
from rarible_marketplace_indexer.event.abstract_action import AbstractOrderListEvent
from rarible_marketplace_indexer.event.abstract_action import AbstractOrderMatchEvent
from rarible_marketplace_indexer.event.dto import CancelDto
from rarible_marketplace_indexer.event.dto import ListDto
from rarible_marketplace_indexer.event.dto import MatchDto
from rarible_marketplace_indexer.event.dto import TakeDto
from rarible_marketplace_indexer.models import PlatformEnum
from rarible_marketplace_indexer.types.rarible_api_objects.asset.enum import AssetClassEnum
from rarible_marketplace_indexer.types.rarible_exchange.parameter.buy import BuyParameter
from rarible_marketplace_indexer.types.rarible_exchange.parameter.cancel_sale import CancelSaleParameter
from rarible_marketplace_indexer.types.rarible_exchange.parameter.sell import SellParameter
from rarible_marketplace_indexer.types.rarible_exchange.storage import RaribleExchangeStorage
from rarible_marketplace_indexer.types.tezos_objects.asset_value.asset_value import AssetValue
from rarible_marketplace_indexer.types.tezos_objects.asset_value.xtz_value import Xtz
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import ImplicitAccountAddress
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OriginatedAccountAddress


class RaribleAware:
    @classmethod
    def _take_xtz(cls, value: int, asset_bytes: Optional[bytes] = None) -> TakeDto:
        assert asset_bytes is None

        return TakeDto(asset_class=AssetClassEnum.XTZ, contract=None, token_id=None, value=Xtz.from_u_tezos(value))  # noqa

    @classmethod
    def _get_contract(cls, asset_bytes: bytes, offset: int) -> OriginatedAccountAddress:
        return OriginatedAccountAddress(b58encode_check(b'\x02Zy' + asset_bytes[offset : offset + 20]).decode())

    @classmethod
    def _take_fa12(cls, value: int, asset_bytes: bytes) -> TakeDto:
        return TakeDto(
            asset_class=AssetClassEnum.FUNGIBLE_TOKEN,  # noqa
            contract=cls._get_contract(asset_bytes, 7),
            token_id=0,
            value=AssetValue(value),
        )

    @classmethod
    def _get_token_id(cls, asset_bytes: bytes) -> int:
        data, token_id, length = asset_bytes[31:], 0, 1

        while data[length - 1] & 0b10000000 != 0:
            length += 1

        for i in range(length - 1, 0, -1):
            token_id <<= 7
            token_id |= data[i] & 0b01111111

        token_id <<= 6
        token_id |= data[0] & 0b00111111

        if (data[0] & 0b01000000) != 0:
            token_id = -token_id

        return token_id

    @classmethod
    def _take_fa2(cls, value: int, asset_bytes: bytes) -> TakeDto:
        return TakeDto(
            asset_class=AssetClassEnum.FUNGIBLE_TOKEN,  # noqa
            contract=cls._get_contract(asset_bytes, 9),
            token_id=cls._get_token_id(asset_bytes),
            value=AssetValue(value),
        )

    unpack_map: Dict[int, Callable] = {
        0: _take_xtz,
        1: _take_fa12,
        2: _take_fa2,
    }

    @staticmethod
    def get_order_hash(contract: OriginatedAccountAddress, token_id: int, seller: ImplicitAccountAddress) -> str:
        return uuid5(namespace=uuid.NAMESPACE_OID, name=f'{contract}:{token_id}@{seller}').hex

    @classmethod
    def get_take_dto(cls, sale_type: int, value: int, asset_bytes: Optional[bytes] = None) -> TakeDto:
        function = cls.unpack_map.get(sale_type)

        return function(value, asset_bytes)


class RaribleOrderListEvent(AbstractOrderListEvent):
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
            seller=ImplicitAccountAddress(transaction.data.sender_address),
        )

        return ListDto(
            internal_order_id=internal_order_id,
            maker=ImplicitAccountAddress(transaction.data.sender_address),
            contract=OriginatedAccountAddress(transaction.parameter.s_asset_contract),
            token_id=int(transaction.parameter.s_asset_token_id),
            amount=AssetValue(transaction.parameter.s_sale.sale_asset_qty),
            object_price=Xtz.from_u_tezos(transaction.parameter.s_sale.sale_amount),
        )


class RaribleOrderCancelEvent(AbstractOrderCancelEvent):
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


class RaribleOrderMatchEvent(AbstractOrderMatchEvent):
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
