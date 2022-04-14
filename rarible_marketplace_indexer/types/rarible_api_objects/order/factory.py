from rarible_marketplace_indexer.models import Order
from rarible_marketplace_indexer.types.rarible_api_objects.asset.asset import Asset
from rarible_marketplace_indexer.types.rarible_api_objects.order.order import RaribleApiOrder


class OrderFactory:
    @staticmethod
    def build(order: Order) -> RaribleApiOrder:
        return RaribleApiOrder(
            id=order.id,
            network=order.network,
            fill=order.fill,
            platform=order.platform,
            status=order.status,
            started_at=order.started_at,
            ended_at=order.ended_at,
            make_stock=order.make_stock,
            cancelled=order.cancelled,
            created_at=order.created_at,
            last_updated_at=order.last_updated_at,
            make_price=order.make_price,
            maker=order.maker,
            taker=order.taker,
            make=Asset.make_from_model(order),
            take=Asset.take_from_model(order),
            salt=order.salt,
        )
