from typing import Optional
from typing import Union

from pydantic import BaseModel


def kafka_value_serializer(value: BaseModel, indent: Optional[int] = None, sort_keys: bool = False) -> bytes:
    return value.json(by_alias=True, indent=indent, sort_keys=sort_keys).encode()


def kafka_key_serializer(key: Union[int, str]) -> bytes:
    return str(key).encode()
