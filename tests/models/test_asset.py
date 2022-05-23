import pytest
from _pytest.fixtures import SubRequest
from pydantic import parse_obj_as

from rarible_marketplace_indexer.models import OrderModel
from rarible_marketplace_indexer.types.rarible_api_objects.asset.asset import Asset


class TestAsset:
    @pytest.fixture(
        params=[
            {
                'asset_type': {'asset_class': 'XTZ'},
                'asset_value': '10.0000011',
            },
            {
                'asset_type': {'asset_class': 'TEZOS_MT', 'contract': 'KT1HbQepzV1nVGg8QVznG7z4RcHseD5kwqBn', 'token_id': 42},
                'asset_value': '127_000_000_000_000_000_000_000_000_000.00000111111',
            },
            {
                'asset_type': {'asset_class': 'TEZOS_NFT', 'contract': 'KT1FvqJwEDWb1Gwc55Jd1jjTHRVWbYKUUpyq', 'token_id': 42},
                'asset_value': '155.0000000000_1111111111_2234567890_0000360890_1234567890',
            },
        ]
    )
    def asset_data(self, request: SubRequest) -> dict:
        return request.param

    def test_pydantic_discriminator(self, asset_data):
        asset = parse_obj_as(Asset, asset_data)
        assert asset

    def test_from_order(self, asset_data):
        order = OrderModel(
            make_asset_class=asset_data['asset_type']['asset_class'],
            make_contract=asset_data['asset_type'].get('contract'),
            make_token_id=asset_data['asset_type'].get('token_id'),
            make_value=asset_data['asset_value'],
        )
        asset = Asset.make_from_model(order)
        assert asset
