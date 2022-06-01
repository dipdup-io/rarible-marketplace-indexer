import uuid
from typing import Dict
from typing import Optional
from uuid import uuid5

from base58 import b58encode_check
from dipdup.datasources.tzkt.datasource import TzktDatasource
from dipdup.models import Transaction

from rarible_marketplace_indexer.event.abstract_action import AbstractOrderCancelEvent, AbstractPutBidEvent, \
    AbstractAcceptBidEvent, AbstractAcceptFloorBidEvent
from rarible_marketplace_indexer.event.abstract_action import AbstractOrderListEvent
from rarible_marketplace_indexer.event.abstract_action import AbstractOrderMatchEvent
from rarible_marketplace_indexer.event.dto import CancelDto, BidDto, AcceptBidDto, AcceptFloorBidDto
from rarible_marketplace_indexer.event.dto import ListDto
from rarible_marketplace_indexer.event.dto import MakeDto
from rarible_marketplace_indexer.event.dto import MatchDto
from rarible_marketplace_indexer.event.dto import TakeDto
from rarible_marketplace_indexer.models import PlatformEnum, TransactionTypeEnum
from rarible_marketplace_indexer.types.rarible_api_objects.asset.enum import AssetClassEnum
from rarible_marketplace_indexer.types.rarible_bids.parameter.put_bid import PutBidParameter, PutFloorBidParameter, \
    AcceptBidParameter, AcceptFloorBidParameter
from rarible_marketplace_indexer.types.rarible_bids.storage import RaribleBidsStorage
from rarible_marketplace_indexer.types.rarible_exchange.parameter.buy import BuyParameter
from rarible_marketplace_indexer.types.rarible_exchange.parameter.cancel_sale import CancelSaleParameter
from rarible_marketplace_indexer.types.rarible_exchange.parameter.sell import SellParameter
from rarible_marketplace_indexer.types.rarible_exchange.storage import RaribleExchangeStorage
from rarible_marketplace_indexer.types.tezos_objects.asset_value.asset_value import AssetValue
from rarible_marketplace_indexer.types.tezos_objects.asset_value.xtz_value import Xtz
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import ImplicitAccountAddress
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OriginatedAccountAddress


class RaribleAware:
    unpack_map: Dict[int, str] = {
        0: '_take_xtz',
        1: '_take_fa12',
        2: '_take_fa2',
    }

    @classmethod
    def _get_contract(cls, asset_bytes: bytes, offset: int) -> OriginatedAccountAddress:
        header = bytes.fromhex('025a79')
        return OriginatedAccountAddress(b58encode_check(header + asset_bytes[offset : offset + 20]).decode())

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
    def _take_xtz(cls, value: int, asset_bytes: Optional[bytes] = None) -> TakeDto:
        assert not asset_bytes

        return TakeDto(asset_class=AssetClassEnum.XTZ, contract=None, token_id=None, value=Xtz.from_u_tezos(value))

    @classmethod
    def _take_fa12(cls, value: int, asset_bytes: bytes) -> TakeDto:
        return TakeDto(
            asset_class=AssetClassEnum.FUNGIBLE_TOKEN,
            contract=cls._get_contract(asset_bytes, 7),
            token_id=0,
            value=AssetValue(value),
        )

    @classmethod
    def _take_fa2(cls, value: int, asset_bytes: bytes) -> TakeDto:
        return TakeDto(
            asset_class=AssetClassEnum.FUNGIBLE_TOKEN,
            contract=cls._get_contract(asset_bytes, 9),
            token_id=cls._get_token_id(asset_bytes),
            value=AssetValue(value),
        )

    @staticmethod
    def get_order_hash(contract: OriginatedAccountAddress, token_id: int, seller: ImplicitAccountAddress, asset_class: str = None, asset: str = None) -> str:
        return uuid5(namespace=uuid.NAMESPACE_OID, name=f'{TransactionTypeEnum.SALE}-{contract}:{token_id}@{seller}/{asset_class}-{asset}').hex

    @staticmethod
    def get_bid_hash(contract: OriginatedAccountAddress, token_id: int, bidder: ImplicitAccountAddress, asset_class: str = None, asset: str = None) -> str:
        return uuid5(namespace=uuid.NAMESPACE_OID, name=f'{TransactionTypeEnum.BID}-{contract}:{token_id}@{bidder}/{asset_class}-{asset}').hex

    @staticmethod
    def get_floor_bid_hash(contract: OriginatedAccountAddress, bidder: ImplicitAccountAddress, asset_class: str = None, asset: str = None) -> str:
        return uuid5(namespace=uuid.NAMESPACE_OID, name=f'{TransactionTypeEnum.FLOOR_BID}-{contract}@{bidder}/{asset_class}-{asset}').hex


    @classmethod
    def get_take_dto(cls, sale_type: int, value: int, asset_bytes: Optional[bytes] = None) -> TakeDto:
        method_name = cls.unpack_map.get(sale_type)
        take_method = getattr(cls, method_name)

        return take_method(value, asset_bytes)


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
            asset_class=transaction.parameter.s_sale_type,
            asset=transaction.parameter.s_sale_asset
        )

        take = RaribleAware.get_take_dto(
            sale_type=int(transaction.parameter.s_sale_type),
            value=int(transaction.parameter.s_sale.sale_amount),
            asset_bytes=bytes.fromhex(transaction.parameter.s_sale_asset),
        )
        make_value = AssetValue(transaction.parameter.s_sale.sale_asset_qty)
        make_price = AssetValue(take.value / make_value)

        return ListDto(
            internal_order_id=internal_order_id,
            maker=ImplicitAccountAddress(transaction.data.sender_address),
            make_price=make_price,
            make=MakeDto(
                asset_class=AssetClassEnum.FUNGIBLE_TOKEN,
                contract=OriginatedAccountAddress(transaction.parameter.s_asset_contract),
                token_id=int(transaction.parameter.s_asset_token_id),
                value=make_value,
            ),
            take=take,
        )


class RaribleOrderCancelEvent(AbstractOrderCancelEvent):
    platform = PlatformEnum.RARIBLE
    RaribleCancelTransaction = Transaction[CancelSaleParameter, RaribleExchangeStorage]

    @staticmethod
    def _get_cancel_dto(transaction: RaribleCancelTransaction, datasource: TzktDatasource) -> CancelDto:
        internal_order_id = RaribleAware.get_order_hash(
            contract=OriginatedAccountAddress(transaction.parameter.cs_asset_contract),
            token_id=int(transaction.parameter.cs_asset_token_id),
            seller=ImplicitAccountAddress(transaction.data.sender_address),
            asset_class=transaction.parameter.cs_sale_type,
            asset=transaction.parameter.cs_sale_asset
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
            asset_class=transaction.parameter.b_sale_type,
            asset=transaction.parameter.b_sale_asset
        )

        return MatchDto(
            internal_order_id=internal_order_id,
            match_amount=AssetValue(1),
            match_timestamp=transaction.data.timestamp,
        )

class RariblePutBidEvent(AbstractPutBidEvent):
    platform = PlatformEnum.RARIBLE
    RariblePutBidTransaction = Transaction[PutBidParameter, RaribleBidsStorage]

    @staticmethod
    def _get_bid_dto(
        transaction: RariblePutBidTransaction,
        datasource: TzktDatasource,
    ) -> BidDto:
        internal_order_id = RaribleAware.get_bid_hash(
            contract=OriginatedAccountAddress(transaction.parameter.pb_asset_contract),
            bidder=ImplicitAccountAddress(transaction.data.sender_address),
            token_id=int(transaction.parameter.pb_asset_token_id),
            asset_class=transaction.parameter.pb_bid_type,
            asset=transaction.parameter.pb_bid_asset,
        )

        take = RaribleAware.get_take_dto(
            sale_type=int(transaction.parameter.pb_bid_type),
            value=int(transaction.parameter.pb_bid.bid_amount),
            asset_bytes=bytes.fromhex(transaction.parameter.pb_bid_asset),
        )
        make_value = AssetValue(transaction.parameter.pb_bid.bid_asset_qty)
        take_price = AssetValue(take.value / make_value)

        return BidDto(
            internal_order_id=internal_order_id,
            bidder=ImplicitAccountAddress(transaction.data.sender_address),
            take_price=take_price,
            make=MakeDto(
                asset_class=AssetClassEnum.FUNGIBLE_TOKEN,
                contract=OriginatedAccountAddress(transaction.parameter.pb_asset_contract),
                token_id=int(transaction.parameter.pb_asset_token_id),
                value=make_value,
            ),
            take=take,
        )

class RariblePutFloorBidEvent(AbstractPutBidEvent):
    platform = PlatformEnum.RARIBLE
    RariblePutFloorBidTransaction = Transaction[PutFloorBidParameter, RaribleBidsStorage]

    @staticmethod
    def _get_bid_dto(
        transaction: RariblePutFloorBidTransaction,
        datasource: TzktDatasource,
    ) -> BidDto:
        internal_order_id = RaribleAware.get_floor_bid_hash(
            contract=OriginatedAccountAddress(transaction.parameter.pfb_asset_contract),
            bidder=ImplicitAccountAddress(transaction.data.sender_address),
            asset_class=transaction.parameter.pfb_bid_type,
            asset=transaction.parameter.pfb_bid_asset
        )

        take = RaribleAware.get_take_dto(
            sale_type=int(transaction.parameter.pfb_bid_type),
            value=int(transaction.parameter.pfb_bid.bid_amount),
            asset_bytes=bytes.fromhex(transaction.parameter.pfb_bid_asset),
        )
        make_value = AssetValue(transaction.parameter.pfb_bid.bid_asset_qty)
        take_price = AssetValue(take.value / make_value)

        return BidDto(
            internal_order_id=internal_order_id,
            bidder=ImplicitAccountAddress(transaction.data.sender_address),
            take_price=take_price,
            make=MakeDto(
                asset_class=AssetClassEnum.FUNGIBLE_TOKEN,
                contract=OriginatedAccountAddress(transaction.parameter.pfb_asset_contract),
                token_id=-1,
                value=make_value,
            ),
            take=take,
        )


class RaribleAcceptBidEvent(AbstractAcceptBidEvent):
    platform = PlatformEnum.RARIBLE
    RaribleAcceptBidTransaction = Transaction[AcceptBidParameter, RaribleExchangeStorage]

    @staticmethod
    def _get_accept_bid_dto(transaction: RaribleAcceptBidTransaction, datasource: TzktDatasource) -> AcceptBidDto:
        internal_order_id = RaribleAware.get_bid_hash(
            contract=OriginatedAccountAddress(transaction.parameter.ab_asset_contract),
            token_id=int(transaction.parameter.ab_asset_token_id),
            bidder=ImplicitAccountAddress(transaction.parameter.ab_bidder),
            asset_class=transaction.parameter.ab_bid_type,
            asset=transaction.parameter.ab_bid_asset
        )

        return AcceptBidDto(
            internal_order_id=internal_order_id,
            bidder=ImplicitAccountAddress(transaction.parameter.ab_bidder),
            seller=ImplicitAccountAddress(transaction.data.sender_address),
            match_timestamp=transaction.data.timestamp,
        )


class RaribleAcceptFloorBidEvent(AbstractAcceptFloorBidEvent):
    platform = PlatformEnum.RARIBLE
    RaribleAcceptFloorBidTransaction = Transaction[AcceptFloorBidParameter, RaribleExchangeStorage]

    @staticmethod
    def _get_accept_floor_bid_dto(transaction: RaribleAcceptFloorBidTransaction, datasource: TzktDatasource) -> AcceptFloorBidDto:
        internal_order_id = RaribleAware.get_floor_bid_hash(
            contract=OriginatedAccountAddress(transaction.parameter.afb_asset_contract),
            bidder=ImplicitAccountAddress(transaction.parameter.afb_bidder),
            asset_class=transaction.parameter.afb_bid_type,
            asset=transaction.parameter.afb_bid_asset
        )

        return AcceptFloorBidDto(
            internal_order_id=internal_order_id,
            token_id=int(transaction.parameter.afb_asset_token_id),
            bidder=ImplicitAccountAddress(transaction.parameter.afb_bidder),
            seller=ImplicitAccountAddress(transaction.data.sender_address),
            match_timestamp=transaction.data.timestamp,
        )