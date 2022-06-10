from typing import Optional

from humps.main import camelize
from pydantic import BaseModel

from rarible_marketplace_indexer.types.rarible_api_objects.asset.enum import AssetClassEnum
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OriginatedAccountAddress


class AssetDescription(BaseModel):
    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True

    type: AssetClassEnum
    contract: Optional[OriginatedAccountAddress]
    token_id: Optional[str]
