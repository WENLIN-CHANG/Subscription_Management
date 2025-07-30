from fastapi import APIRouter, HTTPException
from typing import Dict
from pydantic import BaseModel
from app.services.exchange_rate_service import ExchangeRateService
from app.models.subscription import Currency

router = APIRouter()
exchange_service = ExchangeRateService()

@router.get("/rates", response_model=Dict[str, float])
async def get_exchange_rates():
    """獲取所有匯率 (以台幣為基準)"""
    try:
        rates = await exchange_service.get_exchange_rates()
        return rates
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"無法獲取匯率: {str(e)}")

@router.get("/rates/{currency}", response_model=float)
async def get_exchange_rate(currency: Currency):
    """獲取特定貨幣匯率 (兌台幣)"""
    try:
        rate = await exchange_service.get_exchange_rate(currency.value)
        return rate
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"無法獲取 {currency.value} 匯率: {str(e)}")

class CurrencyConvertRequest(BaseModel):
    from_currency: Currency
    to_currency: Currency  
    amount: float

@router.post("/convert", response_model=float)
async def convert_currency(request: CurrencyConvertRequest):
    """貨幣轉換"""
    try:
        converted_amount = await exchange_service.convert_currency(
            request.amount, request.from_currency.value, request.to_currency.value
        )
        return converted_amount
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"無法轉換 {request.from_currency.value} 到 {request.to_currency.value}: {str(e)}"
        )