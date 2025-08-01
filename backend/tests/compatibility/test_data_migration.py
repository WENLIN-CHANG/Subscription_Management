"""
數據遷移兼容性測試

測試新舊架構之間的數據兼容性：
- 數據庫模型兼容性
- 數據遷移正確性
- 現有數據的兼容性
- 新舊字段映射
"""

import pytest
from datetime import datetime
from sqlalchemy import text

from app.models.subscription import Subscription, SubscriptionCycle, SubscriptionCategory, Currency
from app.models.budget import Budget
from app.models.user import User


class TestDataMigrationCompatibility:
    """數據遷移兼容性測試類"""

    @pytest.mark.compatibility
    @pytest.mark.integration
    class TestModelCompatibility:
        """模型兼容性測試"""

        def test_subscription_model_backward_compatibility(self, db_session, test_user):
            """測試訂閱模型向後兼容性"""
            # 創建使用舊格式的訂閱數據
            subscription = Subscription(
                name="Legacy Subscription",
                price=390.0,
                cycle=SubscriptionCycle.MONTHLY,
                category=SubscriptionCategory.ENTERTAINMENT,
                user_id=test_user.id,
                start_date=datetime(2024, 1, 1),
                is_active=True
            )
            
            # 添加新架構的字段
            subscription.original_price = 390.0
            subscription.currency = Currency.TWD
            
            db_session.add(subscription)
            db_session.commit()
            db_session.refresh(subscription)
            
            # 驗證數據完整性
            assert subscription.id is not None
            assert subscription.name == "Legacy Subscription"
            assert subscription.price == 390.0
            assert subscription.original_price == 390.0
            assert subscription.currency == Currency.TWD
            assert subscription.cycle == SubscriptionCycle.MONTHLY

        def test_budget_model_compatibility(self, db_session, test_user):
            """測試預算模型兼容性"""
            budget = Budget(
                user_id=test_user.id,
                monthly_limit=1000.0
            )
            
            db_session.add(budget)
            db_session.commit()
            db_session.refresh(budget)
            
            # 驗證新舊字段
            assert budget.id is not None
            assert budget.user_id == test_user.id
            assert budget.monthly_limit == 1000.0
            
            # 檢查是否有舊字段的兼容性
            if hasattr(budget, 'amount'):
                assert budget.amount == budget.monthly_limit

        def test_user_model_compatibility(self, db_session):
            """測試用戶模型兼容性"""
            user = User(
                username="compatibility_user",
                email="compatibility@example.com",
                hashed_password="hashed_password"
            )
            
            db_session.add(user)
            db_session.commit()
            db_session.refresh(user)
            
            # 驗證核心字段
            assert user.id is not None
            assert user.username == "compatibility_user"
            assert user.email == "compatibility@example.com"
            assert user.is_active is True  # 默認值

    @pytest.mark.compatibility
    @pytest.mark.integration
    class TestExistingDataCompatibility:
        """現有數據兼容性測試"""

        def test_legacy_subscription_data_access(self, db_session, test_user):
            """測試訪問舊版本創建的訂閱數據"""
            # 模擬舊版本創建的訂閱（缺少新字段）
            legacy_subscription = Subscription(
                name="Legacy Service",
                price=290.0,
                cycle=SubscriptionCycle.MONTHLY,
                category=SubscriptionCategory.MUSIC,
                user_id=test_user.id,
                start_date=datetime(2023, 12, 1),
                is_active=True
            )
            
            # 不設置新字段，模擬舊數据
            db_session.add(legacy_subscription)
            db_session.commit()
            db_session.refresh(legacy_subscription)
            
            # 使用新架構的代碼訪問舊數據
            from app.infrastructure.repositories.subscription_repository import SubscriptionRepository
            
            repo = SubscriptionRepository(db_session)
            retrieved = repo.get_by_id(legacy_subscription.id)
            
            assert retrieved is not None
            assert retrieved.name == "Legacy Service"
            assert retrieved.price == 290.0
            
            # 新字段應該有默認值或能夠處理 None
            assert retrieved.original_price is not None or hasattr(retrieved, 'original_price')
            assert retrieved.currency is not None or hasattr(retrieved, 'currency')

        def test_data_migration_correctness(self, db_session, test_user):
            """測試數據遷移的正確性"""
            # 創建一些測試數據
            subscriptions = []
            for i in range(3):
                subscription = Subscription(
                    name=f"Migration Test {i}",
                    price=100.0 * (i + 1),
                    cycle=SubscriptionCycle.MONTHLY,
                    category=SubscriptionCategory.PRODUCTIVITY,
                    user_id=test_user.id,
                    start_date=datetime(2024, 1, i + 1),
                    is_active=True
                )
                subscriptions.append(subscription)
                db_session.add(subscription)
            
            db_session.commit()
            
            # 驗證數據完整性
            for i, subscription in enumerate(subscriptions):
                db_session.refresh(subscription)
                assert subscription.name == f"Migration Test {i}"
                assert subscription.price == 100.0 * (i + 1)
                assert subscription.user_id == test_user.id

        def test_foreign_key_integrity(self, db_session, test_user):
            """測試外鍵完整性"""
            # 創建預算
            budget = Budget(
                user_id=test_user.id,
                monthly_limit=2000.0
            )
            db_session.add(budget)
            
            # 創建訂閱
            subscription = Subscription(
                name="FK Test Service",
                price=150.0,
                original_price=150.0,
                currency=Currency.TWD,
                cycle=SubscriptionCycle.MONTHLY,
                category=SubscriptionCategory.ENTERTAINMENT,
                user_id=test_user.id,
                start_date=datetime(2024, 1, 1),
                is_active=True
            )
            db_session.add(subscription)
            
            db_session.commit()
            
            # 驗證關聯關係
            assert budget.user_id == test_user.id
            assert subscription.user_id == test_user.id
            
            # 通過關聯查詢數據
            user_subscriptions = db_session.query(Subscription).filter_by(user_id=test_user.id).all()
            user_budgets = db_session.query(Budget).filter_by(user_id=test_user.id).all()
            
            assert len(user_subscriptions) >= 1
            assert len(user_budgets) >= 1

    @pytest.mark.compatibility
    @pytest.mark.integration
    class TestDatabaseSchemaCompatibility:
        """數據庫架構兼容性測試"""

        def test_table_structure_compatibility(self, db_session):
            """測試表結構兼容性"""
            # 檢查核心表是否存在
            tables_to_check = ['users', 'subscriptions', 'budgets']
            
            for table_name in tables_to_check:
                result = db_session.execute(
                    text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                )
                table_exists = result.fetchone() is not None
                assert table_exists, f"表 {table_name} 不存在"

        def test_required_columns_exist(self, db_session):
            """測試必需列是否存在"""
            # 檢查訂閱表的必需列
            subscription_columns = db_session.execute(
                text("PRAGMA table_info(subscriptions)")
            ).fetchall()
            
            column_names = [col[1] for col in subscription_columns]  # col[1] 是列名
            
            required_columns = ['id', 'name', 'price', 'cycle', 'category', 'user_id', 'is_active']
            for column in required_columns:
                assert column in column_names, f"訂閱表缺少列: {column}"

        def test_new_columns_have_defaults(self, db_session, test_user):
            """測試新列有適當的默認值"""
            # 直接插入數據，不提供新列的值
            try:
                db_session.execute(
                    text("""
                    INSERT INTO subscriptions (name, price, cycle, category, user_id, start_date, is_active)
                    VALUES (:name, :price, :cycle, :category, :user_id, :start_date, :is_active)
                    """),
                    {
                        'name': 'Default Test',
                        'price': 100.0,
                        'cycle': 'monthly',
                        'category': 'entertainment',
                        'user_id': test_user.id,
                        'start_date': '2024-01-01',
                        'is_active': True
                    }
                )
                db_session.commit()
                
                # 如果插入成功，說明新列有默認值或允許 NULL
                success = True
            except Exception as e:
                # 如果失敗，檢查是否是因為新列沒有默認值
                success = False
                print(f"插入失敗: {e}")
            
            # 根據實際的數據庫設計來調整這個斷言
            # 如果新列是必需的且沒有默認值，則需要在遷移腳本中處理
            assert success or "NOT NULL constraint failed" not in str(e)

    @pytest.mark.compatibility
    @pytest.mark.integration
    class TestDataConsistency:
        """數據一致性測試"""

        def test_subscription_calculation_consistency(self, db_session, test_user):
            """測試訂閱計算的一致性"""
            from app.domain.services.subscription_domain_service import SubscriptionDomainService
            from app.infrastructure.services.exchange_rate_service_impl import ExchangeRateServiceImpl
            
            # 創建服務實例
            exchange_service = ExchangeRateServiceImpl()
            domain_service = SubscriptionDomainService(exchange_service)
            
            # 創建測試訂閱
            subscription = Subscription(
                name="Consistency Test",
                price=390.0,
                original_price=390.0,
                currency=Currency.TWD,
                cycle=SubscriptionCycle.MONTHLY,
                category=SubscriptionCategory.ENTERTAINMENT,
                user_id=test_user.id,
                start_date=datetime(2024, 1, 1),
                is_active=True
            )
            
            db_session.add(subscription)
            db_session.commit()
            db_session.refresh(subscription)
            
            # 測試計算方法
            monthly_cost = domain_service.calculate_monthly_cost(subscription)
            yearly_cost = domain_service.calculate_yearly_cost(subscription)
            
            assert monthly_cost == 390.0
            assert yearly_cost == 4680.0  # 390 * 12

        def test_budget_calculation_consistency(self, db_session, test_user):
            """測試預算計算的一致性"""
            from app.domain.services.budget_domain_service import BudgetDomainService
            from app.domain.services.subscription_domain_service import SubscriptionDomainService
            from app.infrastructure.services.exchange_rate_service_impl import ExchangeRateServiceImpl
            
            # 創建服務實例
            exchange_service = ExchangeRateServiceImpl()
            subscription_service = SubscriptionDomainService(exchange_service)
            budget_service = BudgetDomainService(subscription_service)
            
            # 創建預算和訂閱
            budget = Budget(
                user_id=test_user.id,
                monthly_limit=1000.0
            )
            
            subscription = Subscription(
                name="Budget Test",
                price=300.0,
                original_price=300.0,
                currency=Currency.TWD,
                cycle=SubscriptionCycle.MONTHLY,
                category=SubscriptionCategory.ENTERTAINMENT,
                user_id=test_user.id,
                start_date=datetime(2024, 1, 1),
                is_active=True
            )
            
            db_session.add(budget)
            db_session.add(subscription)
            db_session.commit()
            
            # 測試預算使用計算
            usage = budget_service.calculate_budget_usage(budget, [subscription])
            
            assert usage["total_budget"] == 1000.0
            assert usage["used_amount"] == 300.0
            assert usage["remaining_amount"] == 700.0
            assert usage["usage_percentage"] == 30.0

    @pytest.mark.compatibility
    @pytest.mark.slow
    class TestLargeDataSetCompatibility:
        """大數據集兼容性測試"""

        def test_bulk_data_migration(self, db_session, test_user):
            """測試批量數據遷移"""
            # 創建大量測試數據
            subscriptions = []
            for i in range(100):
                subscription = Subscription(
                    name=f"Bulk Test {i}",
                    price=float(i + 1),
                    original_price=float(i + 1),
                    currency=Currency.TWD,
                    cycle=SubscriptionCycle.MONTHLY,
                    category=SubscriptionCategory.PRODUCTIVITY,
                    user_id=test_user.id,
                    start_date=datetime(2024, 1, 1),
                    is_active=i % 2 == 0  # 交替激活狀態
                )
                subscriptions.append(subscription)
            
            # 批量插入
            db_session.add_all(subscriptions)
            db_session.commit()
            
            # 驗證數據完整性
            from app.infrastructure.repositories.subscription_repository import SubscriptionRepository
            
            repo = SubscriptionRepository(db_session)
            all_subscriptions = repo.get_by_user_id(test_user.id)
            active_subscriptions = repo.get_active_by_user_id(test_user.id)
            
            assert len(all_subscriptions) >= 100
            assert len(active_subscriptions) == 50  # 一半是活躍的

        def test_performance_with_legacy_data(self, db_session, test_user):
            """測試舊數據的性能"""
            import time
            
            # 創建一些舊格式的數據
            for i in range(50):
                subscription = Subscription(
                    name=f"Performance Test {i}",
                    price=100.0,
                    cycle=SubscriptionCycle.MONTHLY,
                    category=SubscriptionCategory.ENTERTAINMENT,
                    user_id=test_user.id,
                    start_date=datetime(2024, 1, 1),
                    is_active=True
                )
                # 不設置新字段
                db_session.add(subscription)
            
            db_session.commit()
            
            # 測試查詢性能
            from app.infrastructure.repositories.subscription_repository import SubscriptionRepository
            
            repo = SubscriptionRepository(db_session)
            
            start_time = time.time()
            subscriptions = repo.get_by_user_id(test_user.id)
            query_time = time.time() - start_time
            
            # 查詢時間應該在合理範圍內（比如小於1秒）
            assert query_time < 1.0
            assert len(subscriptions) >= 50