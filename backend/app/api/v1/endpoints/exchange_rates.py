from typing import Dict
from fastapi import APIRouter, Depends, Request

from app.common.responses import ApiResponse
from app.services.exchange_rate_service import ExchangeRateService
from app.core.rate_limiter import read_rate_limit

router = APIRouter()

@router.get("/rates", response_model=ApiResponse[Dict[str, float]])
@read_rate_limit()
async def get_exchange_rates(
    request: Request,
    base_currency: str = "TWD"
):
    """獲取匯率信息"""
    service = ExchangeRateService()
    
    # 獲取支持的貨幣列表
    supported_currencies = await service.get_supported_currencies()
    rates = {}
    
    for currency_code in supported_currencies.keys():
        if currency_code != base_currency:
            try:
                rate = await service.get_exchange_rate(base_currency, currency_code)
                rates[currency_code] = float(rate)
            except Exception:
                rates[currency_code] = None
    
    return ApiResponse.success(
        data=rates,
        message=f"成功獲取以 {base_currency} 為基準的匯率"
    )

@router.get("/currencies", response_model=ApiResponse[Dict[str, str]])
@read_rate_limit()
async def get_supported_currencies(request: Request):
    """獲取支持的貨幣列表"""
    service = ExchangeRateService()
    currencies = await service.get_supported_currencies()
    
    return ApiResponse.success(
        data=currencies,
        message="成功獲取支持的貨幣列表"
    )

@router.get("/convert", response_model=ApiResponse[Dict[str, float]])
@read_rate_limit()
async def convert_currency(
    request: Request,
    amount: float,
    from_currency: str,
    to_currency: str
):
    """貨幣轉換"""
    service = ExchangeRateService()
    
    converted_amount = await service.convert_currency(amount, from_currency, to_currency)
    exchange_rate = await service.get_exchange_rate(from_currency, to_currency)
    
    result = {
        "original_amount": amount,
        "converted_amount": converted_amount,
        "from_currency": from_currency,
        "to_currency": to_currency,
        "exchange_rate": float(exchange_rate)
    }
    
    return ApiResponse.success(
        data=result,
        message=f"成功轉換 {amount} {from_currency} 為 {converted_amount} {to_currency}"
    )