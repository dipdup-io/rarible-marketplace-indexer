import uuid

from humps.main import camelize
from pydantic import BaseModel
from pydantic import Field


class AbstractRaribleApiObject(BaseModel):
    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True

    _id_prefix = 'tezos'
    _kafka_topic: str
    id: uuid.UUID
    network: str

    @property
    def kafka_topic(self) -> str:
        return f'{self._kafka_topic}_{self.network}'
