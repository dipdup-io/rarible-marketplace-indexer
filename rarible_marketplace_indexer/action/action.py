from dipdup.datasources.tzkt.datasource import TzktDatasource
from dipdup.models import Transaction


class ListActionInterface:
    @staticmethod
    async def handle(transaction: Transaction, datasource: TzktDatasource):
        raise NotImplementedError


class CancelActionInterface:
    @staticmethod
    async def handle(transaction: Transaction, datasource: TzktDatasource):
        raise NotImplementedError


class MatchActionInterface:
    @staticmethod
    async def handle(transaction: Transaction, datasource: TzktDatasource):
        raise NotImplementedError
