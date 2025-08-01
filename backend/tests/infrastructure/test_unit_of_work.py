"""
Unit of Work 測試

測試事務管理和 Repository 協調：
- 事務生命週期管理
- Repository 實例化
- 提交和回滾操作
- 上下文管理器
- 異常處理
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.infrastructure.unit_of_work import SQLAlchemyUnitOfWork
from app.domain.interfaces.repositories import IUserRepository, ISubscriptionRepository, IBudgetRepository


class TestSQLAlchemyUnitOfWork:
    """SQLAlchemy Unit of Work 測試類"""

    @pytest.fixture
    def mock_session(self):
        """模擬資料庫會話"""
        return Mock(spec=Session)

    @pytest.fixture
    def uow(self, mock_session):
        """創建 Unit of Work 實例"""
        return SQLAlchemyUnitOfWork(mock_session)

    @pytest.mark.unit
    @pytest.mark.infrastructure
    class TestRepositoryAccess:
        """Repository 訪問測試"""

        def test_users_repository_lazy_initialization(self, uow, mock_session):
            """測試用戶 Repository 延遲初始化"""
            with patch('app.infrastructure.unit_of_work.UserRepository') as MockUserRepository:
                mock_repo = Mock(spec=IUserRepository)
                MockUserRepository.return_value = mock_repo
                
                # 第一次訪問
                repo1 = uow.users
                MockUserRepository.assert_called_once_with(mock_session)
                assert repo1 == mock_repo
                
                # 第二次訪問應該返回同一個實例
                repo2 = uow.users
                assert repo2 == repo1
                # 不應該再次調用構造函數
                MockUserRepository.assert_called_once()

        def test_subscriptions_repository_lazy_initialization(self, uow, mock_session):
            """測試訂閱 Repository 延遲初始化"""
            with patch('app.infrastructure.unit_of_work.SubscriptionRepository') as MockSubscriptionRepository:
                mock_repo = Mock(spec=ISubscriptionRepository)
                MockSubscriptionRepository.return_value = mock_repo
                
                repo1 = uow.subscriptions
                MockSubscriptionRepository.assert_called_once_with(mock_session)
                assert repo1 == mock_repo
                
                repo2 = uow.subscriptions
                assert repo2 == repo1
                MockSubscriptionRepository.assert_called_once()

        def test_budgets_repository_lazy_initialization(self, uow, mock_session):
            """測試預算 Repository 延遲初始化"""
            with patch('app.infrastructure.unit_of_work.BudgetRepository') as MockBudgetRepository:
                mock_repo = Mock(spec=IBudgetRepository)
                MockBudgetRepository.return_value = mock_repo
                
                repo1 = uow.budgets
                MockBudgetRepository.assert_called_once_with(mock_session)
                assert repo1 == mock_repo
                
                repo2 = uow.budgets
                assert repo2 == repo1
                MockBudgetRepository.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.infrastructure
    class TestTransactionManagement:
        """事務管理測試"""

        def test_begin_transaction(self, uow, mock_session):
            """測試開始事務"""
            assert not uow._transaction_started
            
            uow.begin()
            
            mock_session.begin.assert_called_once()
            assert uow._transaction_started

        def test_begin_transaction_already_started(self, uow, mock_session):
            """測試重複開始事務"""
            uow.begin()
            mock_session.begin.reset_mock()
            
            uow.begin()  # 第二次調用
            
            mock_session.begin.assert_not_called()  # 不應該再次調用

        def test_commit_transaction(self, uow, mock_session):
            """測試提交事務"""
            uow.begin()
            
            uow.commit()
            
            mock_session.commit.assert_called_once()
            assert not uow._transaction_started

        def test_commit_without_transaction(self, uow, mock_session):
            """測試沒有事務時提交"""
            uow.commit()
            
            mock_session.commit.assert_not_called()

        def test_commit_with_sqlalchemy_error(self, uow, mock_session):
            """測試提交時發生 SQLAlchemy 錯誤"""
            uow.begin()
            mock_session.commit.side_effect = SQLAlchemyError("提交錯誤")
            
            with pytest.raises(SQLAlchemyError):
                uow.commit()
            
            # 應該自動回滾
            mock_session.rollback.assert_called_once()
            assert not uow._transaction_started

        def test_rollback_transaction(self, uow, mock_session):
            """測試回滾事務"""
            uow.begin()
            
            uow.rollback()
            
            mock_session.rollback.assert_called_once()
            assert not uow._transaction_started

        def test_rollback_without_transaction(self, uow, mock_session):
            """測試沒有事務時回滾"""
            uow.rollback()
            
            mock_session.rollback.assert_not_called()

        def test_rollback_with_sqlalchemy_error(self, uow, mock_session):
            """測試回滾時發生 SQLAlchemy 錯誤"""
            uow.begin()
            mock_session.rollback.side_effect = SQLAlchemyError("回滾錯誤")
            
            # 回滾錯誤應該被忽略
            uow.rollback()
            
            mock_session.rollback.assert_called_once()
            assert not uow._transaction_started

        def test_close_session(self, uow, mock_session):
            """測試關閉會話"""
            uow.close()
            
            mock_session.close.assert_called_once()

        def test_close_session_with_active_transaction(self, uow, mock_session):
            """測試關閉有活躍事務的會話"""
            uow.begin()
            
            uow.close()
            
            # 應該先回滾再關閉
            mock_session.rollback.assert_called_once()
            mock_session.close.assert_called_once()

        def test_close_session_with_sqlalchemy_error(self, uow, mock_session):
            """測試關閉會話時發生 SQLAlchemy 錯誤"""
            mock_session.close.side_effect = SQLAlchemyError("關閉錯誤")
            
            # 關閉錯誤應該被忽略
            uow.close()
            
            mock_session.close.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.infrastructure
    class TestContextManager:
        """上下文管理器測試"""

        def test_context_manager_success(self, uow, mock_session):
            """測試上下文管理器成功場景"""
            with uow:
                # 進入時應該開始事務
                mock_session.begin.assert_called_once()
                assert uow._transaction_started
            
            # 退出時應該提交和關閉
            mock_session.commit.assert_called_once()
            mock_session.close.assert_called_once()

        def test_context_manager_with_exception(self, uow, mock_session):
            """測試上下文管理器異常場景"""
            try:
                with uow:
                    mock_session.begin.assert_called_once()
                    raise ValueError("測試異常")
            except ValueError:
                pass
            
            # 應該回滾而不是提交
            mock_session.rollback.assert_called_once()
            mock_session.commit.assert_not_called()
            mock_session.close.assert_called_once()

        def test_context_manager_nested_operations(self, uow, mock_session):
            """測試上下文管理器中的嵌套操作"""
            with patch('app.infrastructure.unit_of_work.SubscriptionRepository') as MockRepo:
                mock_repo = Mock()
                MockRepo.return_value = mock_repo
                
                with uow:
                    # 在上下文中訪問 repository
                    repo = uow.subscriptions
                    assert repo == mock_repo
                    
                    # 模擬一些操作
                    mock_repo.create.return_value = Mock()
                    result = mock_repo.create(Mock())
                    assert result is not None
                
                # 驗證事務正確處理
                mock_session.begin.assert_called_once()
                mock_session.commit.assert_called_once()
                mock_session.close.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.infrastructure
    class TestIntegrationScenarios:
        """集成場景測試"""

        def test_typical_usage_pattern(self, uow, mock_session):
            """測試典型使用模式"""
            with patch('app.infrastructure.unit_of_work.SubscriptionRepository') as MockRepo:
                mock_repo = Mock()
                mock_subscription = Mock()
                MockRepo.return_value = mock_repo
                mock_repo.create.return_value = mock_subscription
                
                # 典型的使用模式
                uow.begin()
                try:
                    subscription = uow.subscriptions.create(Mock())
                    assert subscription == mock_subscription
                    uow.commit()
                except Exception:
                    uow.rollback()
                finally:
                    uow.close()
                
                # 驗證調用順序
                mock_session.begin.assert_called_once()
                mock_repo.create.assert_called_once()
                mock_session.commit.assert_called_once()
                mock_session.close.assert_called_once()

        def test_error_recovery_pattern(self, uow, mock_session):
            """測試錯誤恢復模式"""
            with patch('app.infrastructure.unit_of_work.SubscriptionRepository') as MockRepo:
                mock_repo = Mock()
                MockRepo.return_value = mock_repo
                mock_repo.create.side_effect = SQLAlchemyError("數據庫錯誤")
                
                uow.begin()
                try:
                    uow.subscriptions.create(Mock())
                    uow.commit()
                except SQLAlchemyError:
                    uow.rollback()  # 手動回滾
                finally:
                    uow.close()
                
                # 驗證錯誤處理
                mock_session.begin.assert_called_once()
                mock_repo.create.assert_called_once()
                mock_session.commit.assert_not_called()
                mock_session.rollback.assert_called_once()
                mock_session.close.assert_called_once()

        def test_multiple_repository_access(self, uow, mock_session):
            """測試多個 Repository 訪問"""
            with patch('app.infrastructure.unit_of_work.SubscriptionRepository') as MockSubRepo, \
                 patch('app.infrastructure.unit_of_work.BudgetRepository') as MockBudgetRepo, \
                 patch('app.infrastructure.unit_of_work.UserRepository') as MockUserRepo:
                
                mock_sub_repo = Mock()
                mock_budget_repo = Mock()
                mock_user_repo = Mock()
                
                MockSubRepo.return_value = mock_sub_repo
                MockBudgetRepo.return_value = mock_budget_repo
                MockUserRepo.return_value = mock_user_repo
                
                with uow:
                    # 訪問多個 repository
                    sub_repo = uow.subscriptions
                    budget_repo = uow.budgets
                    user_repo = uow.users
                    
                    assert sub_repo == mock_sub_repo
                    assert budget_repo == mock_budget_repo
                    assert user_repo == mock_user_repo
                
                # 驗證所有 repository 都被正確初始化
                MockSubRepo.assert_called_once_with(mock_session)
                MockBudgetRepo.assert_called_once_with(mock_session)
                MockUserRepo.assert_called_once_with(mock_session)