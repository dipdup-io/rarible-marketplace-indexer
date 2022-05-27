from typing import Callable
from typing import Dict
from typing import Tuple

from dipdup.datasources.tzkt.datasource import TzktDatasource
from dipdup.models import TokenTransferData

from rarible_marketplace_indexer.models import ActivityTypeEnum
from rarible_marketplace_indexer.types.rarible_api_objects.activity.token.activity import BaseRaribleApiTokenActivity
from rarible_marketplace_indexer.types.rarible_api_objects.activity.token.activity import RaribleApiTokenActivity
from rarible_marketplace_indexer.types.rarible_api_objects.activity.token.activity import RaribleApiTokenBurnActivity
from rarible_marketplace_indexer.types.rarible_api_objects.activity.token.activity import RaribleApiTokenMintActivity
from rarible_marketplace_indexer.types.rarible_api_objects.activity.token.activity import RaribleApiTokenTransferActivity
from rarible_marketplace_indexer.types.tezos_objects.asset_value.asset_value import AssetValue
from rarible_marketplace_indexer.types.tezos_objects.tezos_object_hash import OriginatedAccountAddress


class RaribleApiTokenActivityFactory:
    @classmethod
    def _build_base_activity(cls, transfer_data: TokenTransferData, datasource: TzktDatasource) -> BaseRaribleApiTokenActivity:
        try:
            value = AssetValue(transfer_data.amount)
        except TypeError:
            value = AssetValue(0)

        transaction_id = list(
            filter(
                bool,
                [
                    transfer_data.tzkt_transaction_id,
                    transfer_data.tzkt_origination_id,
                    transfer_data.tzkt_migration_id,
                ],
            )
        ).pop()

        return BaseRaribleApiTokenActivity(
            network=datasource.network,
            transfer_id=transfer_data.id,
            contract=OriginatedAccountAddress(transfer_data.contract_address),
            token_id=transfer_data.token_id,
            value=value,
            transaction_id=transaction_id,
            date=transfer_data.timestamp,
        )

    @classmethod
    def _build_mint_activity(cls, transfer_data: TokenTransferData, datasource: TzktDatasource) -> RaribleApiTokenMintActivity:
        base = cls._build_base_activity(transfer_data, datasource)
        return RaribleApiTokenMintActivity(
            type=ActivityTypeEnum.TOKEN_MINT,
            owner=transfer_data.to_address,
            **base.dict(),
        )

    @classmethod
    def _build_transfer_activity(cls, transfer_data: TokenTransferData, datasource: TzktDatasource) -> RaribleApiTokenTransferActivity:
        base = cls._build_base_activity(transfer_data, datasource)
        return RaribleApiTokenTransferActivity(
            type=ActivityTypeEnum.TOKEN_TRANSFER,
            transfer_from=transfer_data.from_address,
            owner=transfer_data.to_address,
            **base.dict(),
        )

    @classmethod
    def _build_burn_activity(cls, transfer_data: TokenTransferData, datasource: TzktDatasource) -> RaribleApiTokenBurnActivity:
        base = cls._build_base_activity(transfer_data, datasource)
        return RaribleApiTokenBurnActivity(
            type=ActivityTypeEnum.TOKEN_BURN,
            owner=transfer_data.from_address,
            **base.dict(),
        )

    @classmethod
    def _get_factory_method(cls, transfer_data: TokenTransferData) -> callable:
        method_map: Dict[Tuple[bool, bool], Callable[[TokenTransferData, TzktDatasource], callable]] = {
            (False, True): cls._build_mint_activity,
            (True, True): cls._build_transfer_activity,
            (True, False): cls._build_burn_activity,
        }

        return method_map.get(
            (
                transfer_data.from_address is not None,
                transfer_data.to_address is not None,
            ),
            cls._build_transfer_activity,
        )

    @classmethod
    def build(cls, transfer_data: TokenTransferData, datasource: TzktDatasource) -> RaribleApiTokenActivity:
        factory_method = cls._get_factory_method(transfer_data)

        return factory_method(transfer_data, datasource)
