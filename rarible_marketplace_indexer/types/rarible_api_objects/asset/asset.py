from typing import Literal
from typing import Optional
from typing import Union

from humps.main import camelize
from pydantic import BaseModel
from pydantic import Field
from pydantic import parse_obj_as
from typing_extensions import Annotated

from rarible_marketplace_indexer.models import Activity
from rarible_marketplace_indexer.models import Order
from rarible_marketplace_indexer.types.rarible_api_objects.asset.asset_type import TokenAssetType
from rarible_marketplace_indexer.types.rarible_api_objects.asset.asset_type import XtzAssetType
from rarible_marketplace_indexer.types.rarible_api_objects.asset.enum import AssetClassEnum
from rarible_marketplace_indexer.types.tezos_objects.asset_value.asset_value import AssetValue
from rarible_marketplace_indexer.types.tezos_objects.asset_value.base_value import BaseValue
from rarible_marketplace_indexer.types.tezos_objects.asset_value.xtz_value import Xtz


class AbstractAsset(BaseModel):
    class Config:
        json_encoders = {
            BaseValue: lambda v: str(v),
        }
        alias_generator = camelize
        allow_population_by_field_name = True


class TokenAsset(AbstractAsset):
    _asset_class: Literal[AssetClassEnum.FUNGIBLE_TOKEN, AssetClassEnum.NON_FUNGIBLE_TOKEN, AssetClassEnum.MULTI_TOKEN] = None
    asset_type: TokenAssetType
    asset_value: AssetValue


class XtzAsset(AbstractAsset):
    _asset_class: Literal[AssetClassEnum.XTZ] = None
    asset_type: XtzAssetType
    asset_value: Xtz


class Asset(AbstractAsset):
    __root__: Annotated[Union[TokenAsset, XtzAsset], Field(discriminator_key='_asset_class')]

    @classmethod
    def make_from_model(cls, model: Union[Order, Activity]) -> AbstractAsset:
        asset = parse_obj_as(
            cls,
            {
                'asset_type': {
                    'asset_class': model.make_asset_class,
                    'contract': model.make_contract,
                    'token_id': model.make_token_id,
                },
                'asset_value': model.make_value,
            },
        )
        return asset.__root__

    @classmethod
    def take_from_model(cls, model: Union[Order, Activity]) -> Optional[AbstractAsset]:
        if not model.take_asset_class:
            return None

        asset = parse_obj_as(
            cls,
            {
                'asset_type': {
                    'asset_class': model.take_asset_class,
                    'contract': model.take_contract,
                    'token_id': model.take_token_id,
                },
                'asset_value': model.take_value,
            },
        )
        return asset.__root__
