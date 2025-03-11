from typing import Any, Dict

import requests
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.requests import Request
from pydantic import BaseModel

from pos.core.services.report_service import ReportService
from pos.core.services.sales_service import SalesService
from pos.runner.routers.infra import _Infra

sales_router = APIRouter()
report_router = APIRouter()


def create_sales_service(request: Request) -> SalesService:
    infra: _Infra = request.app.state.infra
    return SalesService(infra.sales_repo())


def create_report_service(request: Request) -> ReportService:
    infra: _Infra = request.app.state.infra
    return ReportService(infra.report_repo(), infra.shift_repo())


class SalesMiddleResponse(BaseModel):
    n_receipts: int
    revenue_gel: float
    revenue_eur: float
    revenue_usd: float


class SalesResponse(BaseModel):
    sales: SalesMiddleResponse


class ReportMiddleResponse(BaseModel):
    shift_id: str
    n_receipts: int
    products: Dict[str, int]
    revenue_gel: float
    revenue_eur: float
    revenue_usd: float


class ReportResponse(BaseModel):
    report: ReportMiddleResponse


def __get_exchange_rate(base_currency: str, target_currency: str) -> Any:
    try:
        # Construct the API URL
        url = f"https://v6.exchangerate-api.com/v6/08e657b005559007ac9f64ae/latest/{base_currency}"

        # Send GET request to the API
        response = requests.get(url)

        # Parse the JSON response
        data = response.json()

        # Check if the request was successful
        if data["result"] == "success":
            # Return the specific currency rate
            return data["conversion_rates"].get(target_currency)
        else:
            print(f"API Error: {data.get('error-type', 'Unknown error')}")
            return None

    except requests.RequestException as e:
        print(f"Network error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


@sales_router.get("", status_code=200, response_model=SalesResponse)
def get_sales(service: SalesService = Depends(create_sales_service)) -> SalesResponse:
    sales = service.get_sales()
    gel_to_usd = __get_exchange_rate("GEL", "USD")

    gel_to_eur = __get_exchange_rate("GEL", "EUR")

    middle_response = SalesMiddleResponse(
        n_receipts=sales.n_receipts,
        revenue_gel=sales.revenue,
        revenue_eur=sales.revenue * gel_to_eur,
        revenue_usd=sales.revenue * gel_to_usd,
    )
    return SalesResponse(sales=middle_response)


@report_router.get("/x-report", status_code=200, response_model=ReportResponse)
def get_x_report(
    shift_id: str = Query(..., description="The ID of the shift"),
    service: ReportService = Depends(create_report_service),
) -> ReportResponse:
    try:
        report = service.get_x_report(shift_id)

        gel_to_usd = __get_exchange_rate("GEL", "USD")
        gel_to_eur = __get_exchange_rate("GEL", "EUR")
        middle_response = ReportMiddleResponse(
            shift_id=report.shift_id,
            n_receipts=report.n_receipts,
            products=report.products,
            revenue_gel=report.revenue,
            revenue_eur=report.revenue * gel_to_eur,
            revenue_usd=report.revenue * gel_to_usd,
        )

        return ReportResponse(report=middle_response)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@report_router.get("/z-report", status_code=200, response_model=ReportResponse)
def get_z_report(
    shift_id: str = Query(..., description="The ID of the shift"),
    service: ReportService = Depends(create_report_service),
) -> ReportResponse:
    try:
        report = service.get_z_report(shift_id)

        gel_to_usd = __get_exchange_rate("GEL", "USD")
        gel_to_eur = __get_exchange_rate("GEL", "EUR")
        middle_response = ReportMiddleResponse(
            shift_id=report.shift_id,
            n_receipts=report.n_receipts,
            products=report.products,
            revenue_gel=report.revenue,
            revenue_eur=report.revenue * gel_to_eur,
            revenue_usd=report.revenue * gel_to_usd,
        )

        return ReportResponse(report=middle_response)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
