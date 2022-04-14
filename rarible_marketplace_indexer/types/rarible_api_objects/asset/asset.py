from typing import Any
from typing import Literal
from typing import Union

from humps import camelize
from pydantic import BaseModel
from pydantic import Field
from typing_extensions import Annotated

from rarible_marketplace_indexer.types.rarible_api_objects.asset.asset_type import TokenAssetType
from rarible_marketplace_indexer.types.rarible_api_objects.asset.asset_type import XtzAssetType
from rarible_marketplace_indexer.types.rarible_api_objects.asset.enum import AssetClassEnum
from rarible_marketplace_indexer.types.tezos_objects.asset_value.asset_value import AssetValue
from rarible_marketplace_indexer.types.tezos_objects.asset_value.base_value import BaseValue
from rarible_marketplace_indexer.types.tezos_objects.asset_value.xtz_value import Xtz


class AbstractAsset(BaseModel):
    class Config:
        fields = {'asset_class': {'exclude': True, 'alias': None, 'alias_priority': 3}}
        json_encoders = {
            BaseValue: lambda v: str(v),
        }
        alias_generator = camelize
        allow_population_by_field_name = True


class TokenAsset(AbstractAsset):
    asset_class: Literal[AssetClassEnum.FUNGIBLE_TOKEN, AssetClassEnum.NON_FUNGIBLE_TOKEN, AssetClassEnum.MULTI_TOKEN] = None
    asset_type: TokenAssetType
    asset_value: AssetValue


class XtzAsset(AbstractAsset):
    asset_class: Literal[AssetClassEnum.XTZ] = None
    asset_type: XtzAssetType
    asset_value: Xtz


class Asset(AbstractAsset):
    __root__: Annotated[Union[TokenAsset, XtzAsset], Field(discriminator='asset_class')]

    def __init__(self, **data: Any) -> None:
        data['__root__']['asset_class'] = data['__root__']['asset_type']['asset_class']
        super().__init__(**data)
