from logging import Logger
from typing import Optional

from aiokafka import AIOKafkaProducer
from pydantic import BaseModel


# noinspection PyMissingConstructor
class NullKafkaProducer(AIOKafkaProducer):
    def __init__(self, logger: Logger, *args, **kwargs):
        self._logger: Logger = logger

    async def start(self):
        pass

    async def send(self, topic: str, value: BaseModel = None, key: Optional[bytes] = None, *args, **kwargs):
        message = {'topic': {'key': key, 'value': value.json(by_alias=True)}}
        self._logger.info(message)
