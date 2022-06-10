import uuid
from typing import Dict
from typing import Optional
from uuid import uuid5

from base58 import b58encode_check
from dipdup.datasources.tzkt.datasource import TzktDatasource
from dipdup.models import Transaction

from rarible_marketplace_indexer.event.abstract_action import AbstractAcceptBidEvent
from rarible_marketplace_indexer.event.abstract_action import AbstractAcceptFloorBidEvent
from rarible_marketplace_indexer.event.abstract_action import AbstractBidCancelEvent
from rarible_marketplace_indexer.event.abstract_action import AbstractCancelAuctionEvent
from rarible_marketplace_indexer.event.abstract_action import AbstractFinishAuctionEvent
from rarible_marketplace_indexer.event.abstract_action import AbstractFloorBidCancelEvent
from rarible_marketplace_indexer.event.abstract_action import AbstractOrderCancelEvent
from rarible_marketplace_indexer.event.abstract_action import AbstractOrderListEvent
from rarible_marketplace_indexer.event.abstract_action import AbstractOrderMatchEvent
from rarible_marketplace_indexer.event.abstract_action import AbstractPutAuctionBidEvent
from rarible_marketplace_indexer.event.abstract_action import AbstractPutBidEvent
from rarible_marketplace_indexer.event.abstract_action import AbstractStartAuctionEvent
from rarible_marketplace_indexer.event.dto import AssetDto
from rarible_marketplace_indexer.event.dto import CancelDto
from rarible_marketplace_indexer.event.dto import FinishAuctionDto
from rarible_marketplace_indexer.event.dto import ListDto
from rarible_marketplace_indexer.event.dto import MakeDto
from rarible_marketplace_indexer.event.dto import MatchDto
from rarible_marketplace_indexer.event.dto import PutAuctionBidDto
from rarible_marketplace_indexer.event.dto import StartAuctionDto
from rarible_marketplace_indexer.event.dto import TakeDto
from rarible_marketplace_indexer.models import PlatformEnum
from rarible_marketplace_indexer.models import TransactionTypeEnum
from rarible_marketplace_indexer.types.rarible_api_objects.asset.enum import AssetClassEnum
from rarible_marketplace_indexer.types.rarible_auctions.parameter.cancel_auction import CancelAuctionParameter
from rarible_marketplace_indexer.types.rarible_auctions.parameter.finish_auction import FinishAuctionParameter
from rarible_marketplace_indexer.types.rarible_auctions.parameter.put_bid import PutBidParameter as PutAuctionBidParameter
from rarible_marketplace_indexer.types.rarible_auctions.parameter.start_auction import StartAuctionParameter
from rarible_marketplace_indexer.types.rarible_auctions.storage import RaribleAuctionsStorage
from rarible_marketplace_indexer.types.rarible_bids.parameter.accept_bid import AcceptBidParameter
from rarible_marketplace_indexer.types.rarible_bids.parameter.accept_floor_bid import AcceptFloorBidParameter
from rarible_marketplace_indexer.types.rarible_bids.parameter.cancel_bid import CancelBidParameter
from rarible_marketplace_indexer.types.rarible_bids.parameter.cancel_floor_bid import CancelFloorBidParameter
from rarible_marketplace_indexer.types.rarible_bids.parameter.put_bid import PutBidParameter
from rarible_marketplace_indexer.types.rarible_bids.parameter.put_floor_bid import PutFloorBidParameter
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
    unpack_map_take: Dict[int, str] = {
        0: '_take_xtz',
        1: '_take_fa12',
        2: '_take_fa2',
    }

    unpack_map_make: Dict[int, str] = {
        0: '_make_xtz',
        1: '_make_fa12',
        2: '_make_fa2',
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

    @classmethod
    def _make_xtz(cls, value: int, asset_bytes: Optional[bytes] = None) -> TakeDto:
        assert not asset_bytes

        return MakeDto(asset_class=AssetClassEnum.XTZ, contract=None, token_id=None, value=Xtz.from_u_tezos(value))

    @classmethod
    def _make_fa12(cls, value: int, asset_bytes: bytes) -> TakeDto:
        return MakeDto(
            asset_class=AssetClassEnum.FUNGIBLE_TOKEN,
            contract=cls._get_contract(asset_bytes, 7),
            token_id=0,
            value=AssetValue(value),
        )

    @classmethod
    def _make_fa2(cls, value: int, asset_bytes: bytes) -> TakeDto:
        return MakeDto(
            asset_class=AssetClassEnum.FUNGIBLE_TOKEN,
            contract=cls._get_contract(asset_bytes, 9),
            token_id=cls._get_token_id(asset_bytes),
            value=AssetValue(value),
        )

    @staticmethod
    def get_order_hash(
        contract: OriginatedAccountAddress, token_id: int, seller: ImplicitAccountAddress, asset_class: str = None, asset: str = None
    ) -> str:
        return uuid5(
            namespace=uuid.NAMESPACE_OID, name=f'{TransactionTypeEnum.SALE}-{contract}:{token_id}@{seller}/{asset_class}-{asset}'
        ).hex

    @staticmethod
    def get_bid_hash(
        contract: OriginatedAccountAddress, token_id: int, bidder: ImplicitAccountAddress, asset_class: str = None, asset: str = None
    ) -> str:
        return uuid5(
            namespace=uuid.NAMESPACE_OID, name=f'{TransactionTypeEnum.BID}-{contract}:{token_id}@{bidder}/{asset_class}-{asset}'
        ).hex

    @staticmethod
    def get_floor_bid_hash(
        contract: OriginatedAccountAddress, bidder: ImplicitAccountAddress, asset_class: str = None, asset: str = None
    ) -> str:
        return uuid5(namespace=uuid.NAMESPACE_OID, name=f'{TransactionTypeEnum.FLOOR_BID}-{contract}@{bidder}/{asset_class}-{asset}').hex

    @staticmethod
    def get_auction_hash(contract: OriginatedAccountAddress, token_id: int, seller: ImplicitAccountAddress) -> str:
        return uuid5(namespace=uuid.NAMESPACE_OID, name=f'{TransactionTypeEnum.AUCTION}-{contract}:{token_id}@{seller}').hex

    @classmethod
    def get_take_dto(cls, sale_type: int, value: int, asset_bytes: Optional[bytes] = None) -> TakeDto:
        method_name = cls.unpack_map_take.get(sale_type)
        take_method = getattr(cls, method_name)

        return take_method(value, asset_bytes)

    @classmethod
    def get_make_dto(cls, sale_type: int, value: int, asset_bytes: Optional[bytes] = None) -> MakeDto:
        method_name = cls.unpack_map_make.get(sale_type)
        make_method = getattr(cls, method_name)

        return make_method(value, asset_bytes)

    @classmethod
    def get_asset(cls, sale_type: int, asset_bytes: Optional[bytes]) -> AssetDto:
        match sale_type:
            case "0":
                return AssetDto(contract=None, token_id=None)
            case "1":
                return AssetDto(contract=cls._get_contract(asset_bytes, 7), token_id=None)
            case "2":
                return AssetDto(contract=cls._get_contract(asset_bytes, 9), token_id=cls._get_token_id(asset_bytes))
            case _:
                raise Exception(f"Could not parse asset {asset_bytes} for type {sale_type}")


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
            asset=transaction.parameter.s_sale_asset,
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
                asset_class=AssetClassEnum.MULTI_TOKEN,
                contract=OriginatedAccountAddress(transaction.parameter.s_asset_contract),
                token_id=int(transaction.parameter.s_asset_token_id),
                value=make_value,
            ),
            take=take,
            start_at=transaction.parameter.s_sale.sale_start,
            end_at=transaction.parameter.s_sale.sale_end,
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
            asset=transaction.parameter.cs_sale_asset,
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
            asset=transaction.parameter.b_sale_asset,
        )

        return MatchDto(
            internal_order_id=internal_order_id,
            match_amount=AssetValue(transaction.parameter.b_amount),
            match_timestamp=transaction.data.timestamp,
            taker=transaction.data.sender_address,
            token_id=None,
        )


class RariblePutBidEvent(AbstractPutBidEvent):
    platform = PlatformEnum.RARIBLE
    RariblePutBidTransaction = Transaction[PutBidParameter, RaribleBidsStorage]

    @staticmethod
    def _get_bid_dto(
        transaction: RariblePutBidTransaction,
        datasource: TzktDatasource,
    ) -> ListDto:
        internal_order_id = RaribleAware.get_bid_hash(
            contract=OriginatedAccountAddress(transaction.parameter.pb_asset_contract),
            bidder=ImplicitAccountAddress(transaction.data.sender_address),
            token_id=int(transaction.parameter.pb_asset_token_id),
            asset_class=transaction.parameter.pb_bid_type,
            asset=transaction.parameter.pb_bid_asset,
        )

        make = RaribleAware.get_make_dto(
            sale_type=int(transaction.parameter.pb_bid_type),
            value=int(transaction.parameter.pb_bid.bid_amount),
            asset_bytes=bytes.fromhex(transaction.parameter.pb_bid_asset),
        )

        take = TakeDto(
            asset_class=AssetClassEnum.MULTI_TOKEN,
            contract=OriginatedAccountAddress(transaction.parameter.pb_asset_contract),
            token_id=int(transaction.parameter.pb_asset_token_id),
            value=AssetValue(transaction.parameter.pb_bid.bid_asset_qty),
        )
        make_price = AssetValue(make.value / take.value)

        return ListDto(
            internal_order_id=internal_order_id,
            maker=ImplicitAccountAddress(transaction.data.sender_address),
            make_price=make_price,
            make=make,
            take=take,
            start_at=transaction.data.timestamp,
            end_at=transaction.parameter.pb_bid.bid_expiry_date,
        )


class RariblePutFloorBidEvent(AbstractPutBidEvent):
    platform = PlatformEnum.RARIBLE
    RariblePutFloorBidTransaction = Transaction[PutFloorBidParameter, RaribleBidsStorage]

    @staticmethod
    def _get_bid_dto(
        transaction: RariblePutFloorBidTransaction,
        datasource: TzktDatasource,
    ) -> ListDto:
        internal_order_id = RaribleAware.get_floor_bid_hash(
            contract=OriginatedAccountAddress(transaction.parameter.pfb_asset_contract),
            bidder=ImplicitAccountAddress(transaction.data.sender_address),
            asset_class=transaction.parameter.pfb_bid_type,
            asset=transaction.parameter.pfb_bid_asset,
        )

        make = RaribleAware.get_make_dto(
            sale_type=int(transaction.parameter.pfb_bid_type),
            value=int(transaction.parameter.pfb_bid.bid_amount),
            asset_bytes=bytes.fromhex(transaction.parameter.pfb_bid_asset),
        )

        take = TakeDto(
            asset_class=AssetClassEnum.COLLECTION,
            contract=OriginatedAccountAddress(transaction.parameter.pfb_asset_contract),
            token_id=None,
            value=AssetValue(transaction.parameter.pfb_bid.bid_asset_qty),
        )
        make_price = AssetValue(make.value / take.value)

        return ListDto(
            internal_order_id=internal_order_id,
            maker=ImplicitAccountAddress(transaction.data.sender_address),
            make_price=make_price,
            make=make,
            take=take,
            start_at=transaction.data.timestamp,
            end_at=transaction.parameter.pfb_bid.bid_expiry_date,
        )


class RaribleAcceptBidEvent(AbstractAcceptBidEvent):
    platform = PlatformEnum.RARIBLE
    RaribleAcceptBidTransaction = Transaction[AcceptBidParameter, RaribleBidsStorage]

    @staticmethod
    def _get_accept_bid_dto(transaction: RaribleAcceptBidTransaction, datasource: TzktDatasource) -> MatchDto:
        internal_order_id = RaribleAware.get_bid_hash(
            contract=OriginatedAccountAddress(transaction.parameter.ab_asset_contract),
            token_id=int(transaction.parameter.ab_asset_token_id),
            bidder=ImplicitAccountAddress(transaction.parameter.ab_bidder),
            asset_class=transaction.parameter.ab_bid_type,
            asset=transaction.parameter.ab_bid_asset,
        )

        return MatchDto(
            internal_order_id=internal_order_id,
            match_timestamp=transaction.data.timestamp,
            taker=transaction.data.sender_address,
            token_id=None,
            match_amount=None,
        )


class RaribleAcceptFloorBidEvent(AbstractAcceptFloorBidEvent):
    platform = PlatformEnum.RARIBLE
    RaribleAcceptFloorBidTransaction = Transaction[AcceptFloorBidParameter, RaribleBidsStorage]

    @staticmethod
    def _get_accept_floor_bid_dto(transaction: RaribleAcceptFloorBidTransaction, datasource: TzktDatasource) -> MatchDto:
        internal_order_id = RaribleAware.get_floor_bid_hash(
            contract=OriginatedAccountAddress(transaction.parameter.afb_asset_contract),
            bidder=ImplicitAccountAddress(transaction.parameter.afb_bidder),
            asset_class=transaction.parameter.afb_bid_type,
            asset=transaction.parameter.afb_bid_asset,
        )

        return MatchDto(
            internal_order_id=internal_order_id,
            match_timestamp=transaction.data.timestamp,
            taker=transaction.data.sender_address,
            token_id=int(transaction.parameter.afb_asset_token_id),
            match_amount=None,
        )


class RaribleBidCancelEvent(AbstractBidCancelEvent):
    platform = PlatformEnum.RARIBLE
    RaribleCancelBidTransaction = Transaction[CancelBidParameter, RaribleBidsStorage]

    @staticmethod
    def _get_cancel_bid_dto(transaction: RaribleCancelBidTransaction, datasource: TzktDatasource) -> CancelDto:
        internal_order_id = RaribleAware.get_bid_hash(
            contract=OriginatedAccountAddress(transaction.parameter.cb_asset_contract),
            token_id=int(transaction.parameter.cb_asset_token_id),
            bidder=ImplicitAccountAddress(transaction.data.sender_address),
            asset_class=transaction.parameter.cb_bid_type,
            asset=transaction.parameter.cb_bid_asset,
        )

        return CancelDto(internal_order_id=internal_order_id)


class RaribleFloorBidCancelEvent(AbstractFloorBidCancelEvent):
    platform = PlatformEnum.RARIBLE
    RaribleCancelFloorBidTransaction = Transaction[CancelFloorBidParameter, RaribleBidsStorage]

    @staticmethod
    def _get_cancel_floor_bid_dto(transaction: RaribleCancelFloorBidTransaction, datasource: TzktDatasource) -> CancelDto:
        internal_order_id = RaribleAware.get_floor_bid_hash(
            contract=OriginatedAccountAddress(transaction.parameter.cfb_asset_contract),
            bidder=ImplicitAccountAddress(transaction.data.sender_address),
            asset_class=transaction.parameter.cfb_bid_type,
            asset=transaction.parameter.cfb_bid_asset,
        )

        return CancelDto(internal_order_id=internal_order_id)


class RaribleStartAuctionEvent(AbstractStartAuctionEvent):
    platform = PlatformEnum.RARIBLE
    RaribleCreateAuctionTransaction = Transaction[StartAuctionParameter, RaribleAuctionsStorage]

    @staticmethod
    def _get_start_auction_dto(
        transaction: RaribleCreateAuctionTransaction,
        datasource: TzktDatasource,
    ) -> StartAuctionDto:
        auction_id = RaribleAware.get_auction_hash(
            contract=OriginatedAccountAddress(transaction.parameter.sa_asset_contract),
            token_id=int(transaction.parameter.sa_asset_token_id),
            seller=ImplicitAccountAddress(transaction.data.sender_address),
        )

        start = transaction.data.timestamp
        if transaction.parameter.sa_auction.auction_args_start_time is not None:
            start = transaction.parameter.sa_auction.auction_args_start_time

        return StartAuctionDto(
            auction_id=auction_id,
            sell_contract=OriginatedAccountAddress(transaction.parameter.sa_asset_contract),
            sell_token_id=int(transaction.parameter.sa_asset_token_id),
            sell_value=int(transaction.parameter.sa_auction.auction_args_sell_asset_amount),
            buy_asset_type=transaction.parameter.sa_auction.auction_args_buy_asset_type,
            buy_asset=RaribleAware.get_asset(
                transaction.parameter.sa_auction.auction_args_buy_asset_type,
                bytes.fromhex(transaction.parameter.sa_auction.auction_args_buy_asset),
            ),
            start_at=start,
            duration=transaction.parameter.sa_auction.auction_args_duration,
            min_price=transaction.parameter.sa_auction.auction_args_minimal_price,
            min_step=transaction.parameter.sa_auction.auction_args_minimal_step,
            buy_price=transaction.parameter.sa_auction.auction_args_buy_out_price,
            max_seller_fees=transaction.parameter.sa_auction.auction_args_max_seller_fees,
        )


class RariblePutAuctionBidEvent(AbstractPutAuctionBidEvent):
    platform = PlatformEnum.RARIBLE
    RariblePutAuctionBidTransaction = Transaction[PutAuctionBidParameter, RaribleAuctionsStorage]

    @staticmethod
    def _get_put_auction_bid_dto(
        transaction: RariblePutAuctionBidTransaction,
        datasource: TzktDatasource,
    ) -> PutAuctionBidDto:
        auction_id = RaribleAware.get_auction_hash(
            contract=OriginatedAccountAddress(transaction.parameter.pb_asset_contract),
            token_id=int(transaction.parameter.pb_asset_id),
            seller=ImplicitAccountAddress(transaction.parameter.pb_asset_seller),
        )

        return PutAuctionBidDto(
            auction_id=auction_id, bidder=transaction.data.sender_address, bid_value=transaction.parameter.pb_bid.bid_amount
        )


class RaribleFinishAuctionEvent(AbstractFinishAuctionEvent):
    platform = PlatformEnum.RARIBLE
    RaribleFinishAuctionTransaction = Transaction[FinishAuctionParameter, RaribleAuctionsStorage]

    @staticmethod
    def _get_finish_auction_dto(
        transaction: RaribleFinishAuctionTransaction,
        datasource: TzktDatasource,
    ) -> FinishAuctionDto:
        auction_id = RaribleAware.get_auction_hash(
            contract=OriginatedAccountAddress(transaction.parameter.fa_asset_contract),
            token_id=int(transaction.parameter.fa_asset_id),
            seller=ImplicitAccountAddress(transaction.parameter.fa_asset_seller),
        )

        return FinishAuctionDto(auction_id=auction_id)


class RaribleCancelAuctionEvent(AbstractCancelAuctionEvent):
    platform = PlatformEnum.RARIBLE
    RaribleCancelAuctionTransaction = Transaction[CancelAuctionParameter, RaribleAuctionsStorage]

    @staticmethod
    def _get_cancel_auction_dto(
        transaction: RaribleCancelAuctionTransaction,
        datasource: TzktDatasource,
    ) -> FinishAuctionDto:
        auction_id = RaribleAware.get_auction_hash(
            contract=OriginatedAccountAddress(transaction.parameter.ca_asset_contract),
            token_id=int(transaction.parameter.ca_asset_id),
            seller=ImplicitAccountAddress(transaction.data.sender_address),
        )

        return FinishAuctionDto(auction_id=auction_id)
