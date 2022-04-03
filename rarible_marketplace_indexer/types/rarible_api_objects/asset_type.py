from enum import Enum
from typing import Literal

from humps import camelize
from pydantic import BaseModel

from rarible_marketplace_indexer.types.tezos_objects.tezos_currency import AssetValue
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OriginatedAccountAddress


class AssetClassEnum(Enum):
    ETH: str = 'ETH'
    XTZ: str = 'XTZ'
    FUNGIBLE_TOKEN: str = 'TEZOS_FT'
    NON_FUNGIBLE_TOKEN: str = 'TEZOS_NFT'
    MULTI_TOKEN: str = 'TEZOS_MT'
    ERC20: str = 'ERC20'
    ERC721: str = 'ERC721'
    ERC1155: str = 'ERC1155'
    ERC721_LAZY: str = 'ERC721_LAZY'
    ERC1155_LAZY: str = 'ERC1155_LAZY'
    COLLECTION: str = 'COLLECTION'
    GEN_ART: str = 'GEN_ART'


class AssetType(BaseModel):
    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True


class XtzAssetType(AssetType):
    asset_class: Literal[AssetClassEnum.XTZ] = AssetClassEnum.XTZ


class AbstractTokenAssetType(AssetType):
    asset_class: AssetClassEnum
    contract: OriginatedAccountAddress
    token_id: int


class FungibleTokenAssetType(AbstractTokenAssetType):
    asset_class: Literal[AssetClassEnum.FUNGIBLE_TOKEN] = AssetClassEnum.FUNGIBLE_TOKEN


class NonFungibleTokenAssetType(AbstractTokenAssetType):
    asset_class: Literal[AssetClassEnum.NON_FUNGIBLE_TOKEN] = AssetClassEnum.NON_FUNGIBLE_TOKEN


class MultiTokenAssetType(AbstractTokenAssetType):
    asset_class: Literal[AssetClassEnum.MULTI_TOKEN] = AssetClassEnum.MULTI_TOKEN


class Asset(BaseModel):
    type: AssetType
    value: AssetValue
