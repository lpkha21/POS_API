from pos.core.models.repositories import (
    CampaignRepository,
    ProductRepository,
    ReceiptRepository,
    ReportRepository,
    SalesRepository,
    ShiftRepository,
)
from pos.infra.database import Database
from pos.infra.sqlite_repositories.campaign_sqlite_repository import (
    CampaignSQLiteRepository,
)
from pos.infra.sqlite_repositories.product_sqlite_repository import (
    ProductSQLiteRepository,
)
from pos.infra.sqlite_repositories.receipt_sqlite_repository import (
    ReceiptSQLiteRepository,
)
from pos.infra.sqlite_repositories.report_sqlite_repository import (
    ReportSQLiteRepository,
)
from pos.infra.sqlite_repositories.sales_sqlite_repository import SalesSqliteRepository
from pos.infra.sqlite_repositories.shift_sqlite_repository import ShiftSQLiteRepository


class Sqlite:
    db = Database()

    def product_repo(self) -> ProductRepository:
        return ProductSQLiteRepository(self.db)

    def campaign_repo(self) -> CampaignRepository:
        return CampaignSQLiteRepository(self.db)

    def receipt_repo(self) -> ReceiptRepository:
        return ReceiptSQLiteRepository(self.db)

    def sales_repo(self) -> SalesRepository:
        return SalesSqliteRepository(self.db)

    def report_repo(self) -> ReportRepository:
        return ReportSQLiteRepository(self.db)

    def shift_repo(self) -> ShiftRepository:
        return ShiftSQLiteRepository(self.db)
