from rarible_marketplace_indexer.models import BidModel
from rarible_marketplace_indexer.types.rarible_api_objects.asset.asset import Asset
from rarible_marketplace_indexer.types.rarible_api_objects.bid.bid import RaribleApiBid


class RaribleApiBidFactory:
    @staticmethod
    def build(bid: BidModel) -> RaribleApiBid:
        return RaribleApiBid(
            id=bid.id,
            network=bid.network,
            platform=bid.platform,
            status=bid.status,
            ended_at=bid.ended_at,
            created_at=bid.created_at,
            last_updated_at=bid.last_updated_at,
            maker=bid.seller,
            taker=bid.bidder,
            make=Asset.make_from_model(bid),
            take=Asset.take_from_model(bid)
        )
