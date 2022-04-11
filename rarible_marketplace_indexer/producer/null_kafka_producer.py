from logging import Logger
from typing import Optional

from aiokafka import AIOKafkaProducer


# noinspection PyMissingConstructor
class NullKafkaProducer(AIOKafkaProducer):
    def __init__(self, logger: Logger):
        self._logger: Logger = logger

    async def send(self, topic: str, value: Optional[bytes] = None, key: Optional[bytes] = None, *args, **kwargs):
        self._logger.debug(
            {
                topic: {
                    key: value,
                }
            }
        )
