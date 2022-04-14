from abc import ABC
from typing import Literal
from typing import Union

from humps import camelize
from pydantic import BaseModel
from pydantic import Field
from typing_extensions import Annotated

from rarible_marketplace_indexer.types.rarible_api_objects.asset.enum import AssetClassEnum
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OriginatedAccountAddress


class AbstractAssetType(BaseModel, ABC):
    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True

    asset_class: AssetClassEnum


class XtzAssetType(AbstractAssetType):
    asset_class: Literal[AssetClassEnum.XTZ]


class AbstractTokenAssetType(AbstractAssetType, ABC):
    contract: OriginatedAccountAddress
    token_id: str


class FungibleTokenAssetType(AbstractTokenAssetType):
    asset_class: Literal[AssetClassEnum.FUNGIBLE_TOKEN]


class NonFungibleTokenAssetType(AbstractTokenAssetType):
    asset_class: Literal[AssetClassEnum.NON_FUNGIBLE_TOKEN]


class MultiTokenAssetType(AbstractTokenAssetType):
    asset_class: Literal[AssetClassEnum.MULTI_TOKEN]


TokenAssetType = Union[FungibleTokenAssetType, NonFungibleTokenAssetType, MultiTokenAssetType]
AssetType = Annotated[Union[XtzAssetType, TokenAssetType], Field(discriminator='asset_class')]
