from fastapi import FastAPI

from pos.infra.sqlite_repositories.sqlite import Sqlite
from pos.runner.routers.campaign_router import router as campaign_router
from pos.runner.routers.product_router import router as product_router
from pos.runner.routers.receipt_router import router as receipt_router
from pos.runner.routers.report_router import report_router, sales_router
from pos.runner.routers.shift_router import router as shift_router


def setup() -> FastAPI:
    api = FastAPI(title="POS System API", version="1.0.0")

    api.state.infra = Sqlite()

    api.include_router(product_router, prefix="/products", tags=["Products"])
    api.include_router(receipt_router, prefix="/receipts", tags=["Receipts"])
    api.include_router(campaign_router, prefix="/campaign", tags=["Campaign"])
    api.include_router(sales_router, prefix="/sales", tags=["Sales"])
    api.include_router(report_router, prefix="/reports", tags=["Report"])
    api.include_router(shift_router, prefix="/shift", tags=["Shift"])

    return api
