from fastapi import APIRouter

from kakeibo_be.api.v1.cash_flows import router as cash_flows_router
from kakeibo_be.api.v1.health_check import router as health_check_router

router = APIRouter()

router.include_router(health_check_router, prefix="/health-check", tags=["Health Check"])
router.include_router(cash_flows_router, prefix="/cash-flows", tags=["Cash Flows"])
