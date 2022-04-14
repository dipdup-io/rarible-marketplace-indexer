from enum import Enum


class AssetClassEnum(str, Enum):
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
