from typing import Union

from pydantic import BaseModel


def kafka_value_serializer(value: BaseModel) -> bytes:
    return value.json(by_alias=True).encode()


def kafka_key_serializer(key: Union[int, str]) -> bytes:
    return str(key).encode()
