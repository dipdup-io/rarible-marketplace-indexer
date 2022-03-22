from enum import Enum
from typing import Literal

from pydantic.dataclasses import dataclass

from rarible_marketplace_indexer.types.tezos_objects.tezos_currency import AssetValue
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OriginatedAccountAddress


class AssetClassEnum(Enum):
    ETH: str = 'ETH'
    XTZ: str = 'XTZ'
    ERC20: str = 'ERC20'
    ERC721: str = 'ERC721'
    ERC1155: str = 'ERC1155'
    ERC721_LAZY: str = 'ERC721_LAZY'
    ERC1155_LAZY: str = 'ERC1155_LAZY'
    CRYPTO_PUNKS: str = 'CRYPTO_PUNKS'
    COLLECTION: str = 'COLLECTION'
    GEN_ART: str = 'GEN_ART'


@dataclass
class AssetType:
    ...


@dataclass
class XtzAssetType(AssetType):
    asset_class: Literal[AssetClassEnum.XTZ]


@dataclass
class CryptoPunksAssetType(AssetType):
    asset_class: Literal[AssetClassEnum.CRYPTO_PUNKS]
    contract: OriginatedAccountAddress
    token_id: int


@dataclass
class Asset:
    type: AssetType
    value: AssetValue
