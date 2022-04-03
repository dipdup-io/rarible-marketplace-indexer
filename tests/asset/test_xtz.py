from decimal import Decimal

import pytest

from rarible_marketplace_indexer.types.tezos_objects.tezos_currency import AssetValue
from rarible_marketplace_indexer.types.tezos_objects.tezos_currency import Xtz


class TestXtz:
    @pytest.fixture(params=(1000, 100, 10, 1, 0.1, 0.01, 0.000001, '0.05', -30, Decimal(15)))
    def valid_tezos_value(self, request) -> Xtz:
        return Xtz(request.param)

    def test_constructor(self, valid_tezos_value):
        assert type(valid_tezos_value) == Xtz

    def test_precision(self, valid_tezos_value):
        assert abs(valid_tezos_value) > 0

    @pytest.mark.parametrize('not_of_value', (0.000_000_1, 1e-7, -0.000_000_1, -1e-7))
    def test_precision_negative(self, not_of_value):
        assert Xtz(not_of_value) == 0

    def test_equation(self, valid_tezos_value):
        assert valid_tezos_value == float(valid_tezos_value)
        assert valid_tezos_value == str(valid_tezos_value)

    @pytest.mark.parametrize(
        'value, expected_str',
        (
            (-42, '-42'),
            (0, '0'),
            (0.000, '0'),
            (13, '13'),
            (100.000001, '100.000001'),
            (-100.000001, '-100.000001'),
            (000.000001, '0.000001'),
            (-000.000001, '-0.000001'),
            (000.0000001, '0'),
            (1e3, '1000'),
        ),
    )
    def test_str(self, value, expected_str):
        xtz = Xtz(value)
        assert str(xtz) == expected_str

    @pytest.mark.parametrize(
        'utz_value, expected',
        (
            (127001, '0.127001'),
            (127001.10, '0.127001'),
            (30_000_000, '30'),
            (500_000_000, '500'),
            ('500_000_000', '500'),
        ),
    )
    def test_from_u_tezos(self, utz_value, expected):
        xtz = Xtz.from_u_tezos(utz_value)
        assert xtz == expected

    def test_arithmetic(self):
        assert (Xtz(5) * AssetValue(3) + Xtz(35)) == 50

    def test_too_many_digits(self):
        """
        see: https://better-call.dev/mainnet/opg/ooiZQuVH8ATmZ6w8JuLvtygy2ScqvoxedJjuvG9NbbL8X318zRq/contents
        """
        huge_value = 4206942069420695000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000  # noqa
        xtz = Xtz(huge_value)
        assert xtz == 0
