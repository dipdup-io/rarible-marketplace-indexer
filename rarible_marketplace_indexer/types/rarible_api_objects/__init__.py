import uuid
from typing import Any

from humps.main import camelize
from pydantic import BaseModel

from rarible_marketplace_indexer.types.tezos_objects.asset_value.base_value import BaseValue


class AbstractRaribleApiObject(BaseModel):
    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True
        json_encoders = {
            BaseValue: lambda v: str(v),
        }

    _id_prefix = 'tezos'
    _kafka_topic: str
    id: uuid.UUID
    network: str

    @property
    def kafka_topic(self) -> str:
        return f'{self._kafka_topic}_{self.network}'

    @classmethod
    def _get_value(cls, v: Any, *args, **kwargs) -> Any:
        if type(v) is int:
            v = str(v)
        return super()._get_value(v, *args, **kwargs)
