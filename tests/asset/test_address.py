from decimal import Decimal

import pytest

from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import ImplicitAccountAddress
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OriginatedAccountAddress


class TestAddressXtz:
    @pytest.fixture(
        params=(
            'tz1QGCWjNpYmcS6T9qFGYSam25e36WeFUCK4',
            'tz1iZ2TPEShFC8TqHsXLA9RXdV7tSv8E3aLe',
            'tz1iZ2TPEShFC8TqHsXLA9RXdV7tSv8E3aLe',
            'tz2iZ2TPEShFC8TqHsXLA9RXdV7tSv8E3aLe',
            'tz3iZ2TPEShFC8TqHsXLA9RXdV7tSv8E3aLe',
        )
    )
    def valid_implicit_address(self, request) -> str:
        return request.param

    @pytest.fixture(
        params=(
            'KT1HbQepzV1nVGg8QVznG7z4RcHseD5kwqBn',
            'KT1FvqJwEDWb1Gwc55Jd1jjTHRVWbYKUUpyq',
            'KT1WvzYHCNBvDSdwafTHv7nJ1dWmZ8GCYuuC',
            'KT1QZ3yLmojkaTaPBoDq9uZ4V1iggoN1bmGk',
        )
    )
    def valid_originated_address(self, request) -> str:
        return request.param

    @pytest.fixture(
        params=(
            'tz4QGCWjNpYmcS6T9qFGYSam25e36WeFUCK4',
            'KT1HbQepzV1nVGg8QVznG7z4RcHseD5kwqBn',
            'tz1foo',
            'bar',
            None,
            42,
        )
    )
    def invalid_implicit_address(self, request) -> str:
        return request.param

    @pytest.fixture(
        params=(
            'tz1QGCWjNpYmcS6T9qFGYSam25e36WeFUCK4',
            'KT2HbQepzV1nVGg8QVznG7z4RcHseD5kwqBn',
            'KT1foo',
            'bar',
            None,
            42,
        )
    )
    def invalid_originated_address(self, request) -> str:
        return request.param

    def test_positive_implicit(self, valid_implicit_address: str):
        address = ImplicitAccountAddress(valid_implicit_address)
        assert ImplicitAccountAddress.validate(address)

    def test_positive_originated(self, valid_originated_address: str):
        address = OriginatedAccountAddress(valid_originated_address)
        assert OriginatedAccountAddress.validate(address)

    def test_negative_implicit(self, invalid_implicit_address: str):
        with pytest.raises(ValueError):
            address = ImplicitAccountAddress(invalid_implicit_address)
            assert ImplicitAccountAddress.validate(address)

    def test_negative_originated(self, invalid_originated_address: str):
        with pytest.raises(ValueError):
            address = OriginatedAccountAddress(invalid_originated_address)
            OriginatedAccountAddress.validate(address)
