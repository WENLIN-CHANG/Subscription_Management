from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Annotated

from app.database.connection import get_db
from app.infrastructure.unit_of_work import SQLAlchemyUnitOfWork
from app.infrastructure.services.exchange_rate_service_impl import ExchangeRateServiceImpl
from app.domain.services.subscription_domain_service import SubscriptionDomainService
from app.domain.services.budget_domain_service import BudgetDomainService
from app.application.services.subscription_application_service import SubscriptionApplicationService
from app.application.services.budget_application_service import BudgetApplicationService
from app.domain.interfaces.repositories import IUnitOfWork
from app.domain.interfaces.services import IExchangeRateService

# 依賴注入類型別名
DatabaseSession = Annotated[Session, Depends(get_db)]

def get_unit_of_work(db: DatabaseSession) -> IUnitOfWork:
    """獲取工作單元"""
    return SQLAlchemyUnitOfWork(db)

def get_exchange_rate_service() -> IExchangeRateService:
    """獲取匯率服務"""
    return ExchangeRateServiceImpl()

def get_subscription_domain_service(
    exchange_service: IExchangeRateService = Depends(get_exchange_rate_service)
) -> SubscriptionDomainService:
    """獲取訂閱領域服務"""
    return SubscriptionDomainService(exchange_service)

def get_budget_domain_service(
    subscription_service: SubscriptionDomainService = Depends(get_subscription_domain_service)
) -> BudgetDomainService:
    """獲取預算領域服務"""
    return BudgetDomainService(subscription_service)

def get_subscription_application_service(
    uow: IUnitOfWork = Depends(get_unit_of_work),
    domain_service: SubscriptionDomainService = Depends(get_subscription_domain_service)
) -> SubscriptionApplicationService:
    """獲取訂閱應用服務"""
    return SubscriptionApplicationService(uow, domain_service)

def get_budget_application_service(
    uow: IUnitOfWork = Depends(get_unit_of_work),
    domain_service: BudgetDomainService = Depends(get_budget_domain_service)
) -> BudgetApplicationService:
    """獲取預算應用服務"""
    return BudgetApplicationService(uow, domain_service)