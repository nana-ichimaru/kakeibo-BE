from fastapi import APIRouter

router = APIRouter()

@router.get("")
def get_cash_flows() -> dict:
    return {"status": "ok"}

@router.post("")
def create_cash_flow() -> dict:
    return {"status": "ok"}

@router.put("")
def update_cash_flow() -> dict:
    return {"status": "ok"}

@router.delete("")
def delete_cash_flow() -> dict:
    return {"status": "ok"}