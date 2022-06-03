from rarible_marketplace_indexer.models import AuctionModel
from rarible_marketplace_indexer.types.rarible_api_objects.asset.asset import Asset
from rarible_marketplace_indexer.types.rarible_api_objects.asset.asset_description import AssetDescription
from rarible_marketplace_indexer.types.rarible_api_objects.auction.auction import RaribleApiAuction
from rarible_marketplace_indexer.types.rarible_api_objects.auction.auction_bid import AuctionBid


class RaribleApiAuctionFactory:
    @staticmethod
    def build(auction: AuctionModel) -> RaribleApiAuction:
        last_bid = None
        if auction.last_bid_bidder is not None:
            last_bid = AuctionBid(buyer=auction.last_bid_bidder, amount=auction.last_bid_amount, date=auction.last_bid_date)
        return RaribleApiAuction(
            id=auction.id,
            platform=auction.platform,
            network=auction.network,
            contract=auction.sell_contract,
            seller=auction.seller,
            sell=Asset.sell_from_auction_model(auction),
            buy=AssetDescription(
                type=auction.buy_asset_class,
                contract=auction.buy_contract,
                token_id=auction.buy_token_id,
            ),
            end_time=auction.end_time,
            minimal_step=auction.minimal_step,
            minimal_price=auction.minimal_price,
            created_at=auction.created_at,
            last_updated_at=auction.last_updated_at,
            buy_price=auction.buy_price,
            status=auction.status,
            ongoing=auction.ongoing,
            hash=auction.auction_id,
            start_at=auction.start_at,
            auction_id=auction.auction_id,
            last_bid=last_bid,
        )
