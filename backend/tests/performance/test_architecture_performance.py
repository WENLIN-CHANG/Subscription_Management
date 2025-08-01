"""
架構性能對比測試

對比新舊架構的性能表現：
- API 響應時間對比
- 內存使用對比
- 並發處理能力對比
- 數據庫查詢性能對比
- 業務邏輯執行效率對比
"""

import pytest
import time
import threading
import psutil
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from statistics import mean, median
from datetime import datetime


class TestArchitecturePerformance:
    """架構性能對比測試類"""

    @pytest.mark.performance
    @pytest.mark.slow
    class TestAPIResponseTime:
        """API 響應時間測試"""

        def measure_response_time(self, client, endpoint, headers=None, method='GET', json_data=None):
            """測量單個請求的響應時間"""
            start_time = time.time()
            
            if method == 'GET':
                response = client.get(endpoint, headers=headers)
            elif method == 'POST':
                response = client.post(endpoint, json=json_data, headers=headers)
            elif method == 'PUT':
                response = client.put(endpoint, json=json_data, headers=headers)
            elif method == 'DELETE':
                response = client.delete(endpoint, headers=headers)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            return response_time, response.status_code

        def test_get_subscriptions_performance_comparison(self, client, new_client, auth_headers, multiple_test_subscriptions):
            """比較獲取訂閱列表的性能"""
            iterations = 10
            old_times = []
            new_times = []
            
            # 測試舊架構
            for _ in range(iterations):
                response_time, status_code = self.measure_response_time(
                    client, "/api/subscriptions", auth_headers
                )
                if status_code == 200:
                    old_times.append(response_time)
            
            # 測試新架構
            for _ in range(iterations):
                response_time, status_code = self.measure_response_time(
                    new_client, "/api/v1/subscriptions/", auth_headers
                )
                if status_code == 200:
                    new_times.append(response_time)
            
            # 分析結果
            if old_times and new_times:
                old_avg = mean(old_times)
                new_avg = mean(new_times)
                old_median = median(old_times)
                new_median = median(new_times)
                
                print(f"\n獲取訂閱列表性能對比:")
                print(f"舊架構 - 平均: {old_avg:.4f}s, 中位數: {old_median:.4f}s")
                print(f"新架構 - 平均: {new_avg:.4f}s, 中位數: {new_median:.4f}s")
                print(f"性能變化: {((new_avg - old_avg) / old_avg * 100):+.2f}%")
                
                # 新架構不應該比舊架構慢太多（允許50%的性能降低）
                assert new_avg < old_avg * 1.5, f"新架構響應時間過慢: {new_avg:.4f}s vs {old_avg:.4f}s"

        def test_create_subscription_performance_comparison(self, client, new_client, auth_headers):
            """比較創建訂閱的性能"""
            iterations = 5
            old_times = []
            new_times = []
            
            # 測試數據
            old_payload = {
                "name": "Performance Test Old",
                "price": 100.0,
                "cycle": "monthly",
                "category": "entertainment",
                "start_date": "2024-01-01"
            }
            
            new_payload = {
                "name": "Performance Test New",
                "original_price": 100.0,
                "currency": "TWD",
                "cycle": "monthly",
                "category": "entertainment",
                "start_date": "2024-01-01T00:00:00"
            }
            
            # 測試舊架構
            for i in range(iterations):
                payload = old_payload.copy()
                payload["name"] = f"Performance Test Old {i}"
                
                response_time, status_code = self.measure_response_time(
                    client, "/api/subscriptions", auth_headers, 'POST', payload
                )
                if status_code in [200, 201]:
                    old_times.append(response_time)
            
            # 測試新架構
            for i in range(iterations):
                payload = new_payload.copy()
                payload["name"] = f"Performance Test New {i}"
                
                response_time, status_code = self.measure_response_time(
                    new_client, "/api/v1/subscriptions/", auth_headers, 'POST', payload
                )
                if status_code in [200, 201]:
                    new_times.append(response_time)
            
            # 分析結果
            if old_times and new_times:
                old_avg = mean(old_times)
                new_avg = mean(new_times)
                
                print(f"\n創建訂閱性能對比:")
                print(f"舊架構 - 平均: {old_avg:.4f}s")
                print(f"新架構 - 平均: {new_avg:.4f}s")
                print(f"性能變化: {((new_avg - old_avg) / old_avg * 100):+.2f}%")
                
                # 創建操作允許更多性能損失，因為涉及更多業務邏輯
                assert new_avg < old_avg * 2.0, f"新架構創建操作過慢: {new_avg:.4f}s vs {old_avg:.4f}s"

        def test_concurrent_requests_performance(self, client, new_client, auth_headers):
            """測試並發請求性能"""
            concurrent_users = 5
            requests_per_user = 3
            
            def make_requests(test_client, endpoint, headers):
                times = []
                for _ in range(requests_per_user):
                    start_time = time.time()
                    response = test_client.get(endpoint, headers=headers)
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        times.append(end_time - start_time)
                    
                    time.sleep(0.1)  # 避免過於頻繁的請求
                
                return times
            
            # 測試舊架構並發性能
            old_results = []
            with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
                futures = [
                    executor.submit(make_requests, client, "/api/subscriptions", auth_headers)
                    for _ in range(concurrent_users)
                ]
                
                for future in as_completed(futures):
                    old_results.extend(future.result())
            
            # 測試新架構並發性能
            new_results = []
            with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
                futures = [
                    executor.submit(make_requests, new_client, "/api/v1/subscriptions/", auth_headers)
                    for _ in range(concurrent_users)
                ]
                
                for future in as_completed(futures):
                    new_results.extend(future.result())
            
            # 分析並發性能
            if old_results and new_results:
                old_avg = mean(old_results)
                new_avg = mean(new_results)
                
                print(f"\n並發請求性能對比 ({concurrent_users} 用戶, 每用戶 {requests_per_user} 請求):")
                print(f"舊架構 - 平均響應時間: {old_avg:.4f}s")
                print(f"新架構 - 平均響應時間: {new_avg:.4f}s")
                
                # 並發情況下新架構不應該顯著變慢
                assert new_avg < old_avg * 2.0, f"新架構並發性能過差: {new_avg:.4f}s vs {old_avg:.4f}s"

    @pytest.mark.performance
    @pytest.mark.slow
    class TestMemoryUsage:
        """內存使用測試"""

        def get_memory_usage(self):
            """獲取當前進程的內存使用情況"""
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            return memory_info.rss / 1024 / 1024  # 轉換為 MB

        def test_memory_usage_comparison(self, client, new_client, auth_headers):
            """比較新舊架構的內存使用"""
            # 記錄初始內存使用
            initial_memory = self.get_memory_usage()
            
            # 使用舊架構執行一系列操作
            old_memory_start = self.get_memory_usage()
            
            for i in range(10):
                client.get("/api/subscriptions", headers=auth_headers)
                if i % 2 == 0:
                    payload = {
                        "name": f"Memory Test {i}",
                        "price": 100.0,
                        "cycle": "monthly",
                        "category": "entertainment",
                        "start_date": "2024-01-01"
                    }
                    client.post("/api/subscriptions", json=payload, headers=auth_headers)
            
            old_memory_end = self.get_memory_usage()
            old_memory_usage = old_memory_end - old_memory_start
            
            # 使用新架構執行相同操作
            new_memory_start = self.get_memory_usage()
            
            for i in range(10):
                new_client.get("/api/v1/subscriptions/", headers=auth_headers)
                if i % 2 == 0:
                    payload = {
                        "name": f"Memory Test New {i}",
                        "original_price": 100.0,
                        "currency": "TWD",
                        "cycle": "monthly",
                        "category": "entertainment",
                        "start_date": "2024-01-01T00:00:00"
                    }
                    new_client.post("/api/v1/subscriptions/", json=payload, headers=auth_headers)
            
            new_memory_end = self.get_memory_usage()
            new_memory_usage = new_memory_end - new_memory_start
            
            print(f"\n內存使用對比:")
            print(f"初始內存: {initial_memory:.2f} MB")
            print(f"舊架構內存增長: {old_memory_usage:.2f} MB")
            print(f"新架構內存增長: {new_memory_usage:.2f} MB")
            
            # 新架構的內存使用不應該比舊架構高太多
            if old_memory_usage > 0:
                memory_ratio = new_memory_usage / old_memory_usage
                print(f"内存使用比率: {memory_ratio:.2f}")
                
                # 允許新架構使用更多內存，但不應該超過3倍
                assert memory_ratio < 3.0, f"新架構內存使用過多: {memory_ratio:.2f}倍"

    @pytest.mark.performance 
    @pytest.mark.slow
    class TestDatabasePerformance:
        """數據庫性能測試"""

        def test_query_performance_comparison(self, db_session, test_user):
            """比較數據庫查詢性能"""
            from app.infrastructure.repositories.subscription_repository import SubscriptionRepository
            from app.models.subscription import Subscription, SubscriptionCycle, SubscriptionCategory, Currency
            
            # 創建大量測試數據
            subscriptions = []
            for i in range(100):
                subscription = Subscription(
                    name=f"Query Test {i}",
                    price=float(i + 1),
                    original_price=float(i + 1),
                    currency=Currency.TWD,
                    cycle=SubscriptionCycle.MONTHLY,
                    category=SubscriptionCategory.ENTERTAINMENT,
                    user_id=test_user.id,
                    start_date=datetime(2024, 1, 1),
                    is_active=i % 2 == 0
                )
                subscriptions.append(subscription)
            
            db_session.add_all(subscriptions)
            db_session.commit()
            
            # 測試 Repository 查詢性能
            repo = SubscriptionRepository(db_session)
            
            # 測試獲取所有訂閱
            start_time = time.time()
            all_subscriptions = repo.get_by_user_id(test_user.id)
            all_query_time = time.time() - start_time
            
            # 測試獲取活躍訂閱
            start_time = time.time()
            active_subscriptions = repo.get_active_by_user_id(test_user.id)
            active_query_time = time.time() - start_time
            
            # 測試按類別查詢
            start_time = time.time()
            category_subscriptions = repo.get_by_category(test_user.id, "entertainment")
            category_query_time = time.time() - start_time
            
            # 測試搜索查詢
            start_time = time.time()
            search_subscriptions = repo.get_by_name_pattern(test_user.id, "Query")
            search_query_time = time.time() - start_time
            
            print(f"\n數據庫查詢性能 (100條記錄):")
            print(f"獲取所有訂閱: {all_query_time:.4f}s ({len(all_subscriptions)} 條)")
            print(f"獲取活躍訂閱: {active_query_time:.4f}s ({len(active_subscriptions)} 條)")
            print(f"按類別查詢: {category_query_time:.4f}s ({len(category_subscriptions)} 條)")
            print(f"搜索查詢: {search_query_time:.4f}s ({len(search_subscriptions)} 條)")
            
            # 查詢時間應該在合理範圍內
            assert all_query_time < 1.0, f"查詢所有訂閱過慢: {all_query_time:.4f}s"
            assert active_query_time < 1.0, f"查詢活躍訂閱過慢: {active_query_time:.4f}s"
            assert category_query_time < 1.0, f"類別查詢過慢: {category_query_time:.4f}s"
            assert search_query_time < 1.0, f"搜索查詢過慢: {search_query_time:.4f}s"

        def test_bulk_operations_performance(self, db_session, test_user):
            """測試批量操作性能"""
            from app.models.subscription import Subscription, SubscriptionCycle, SubscriptionCategory, Currency
            
            # 測試批量插入性能
            bulk_size = 200
            subscriptions = []
            
            start_time = time.time()
            
            for i in range(bulk_size):
                subscription = Subscription(
                    name=f"Bulk Test {i}",
                    price=float(i + 1),
                    original_price=float(i + 1),
                    currency=Currency.TWD,
                    cycle=SubscriptionCycle.MONTHLY,
                    category=SubscriptionCategory.PRODUCTIVITY,
                    user_id=test_user.id,
                    start_date=datetime(2024, 1, 1),
                    is_active=True
                )
                subscriptions.append(subscription)
            
            db_session.add_all(subscriptions)
            db_session.commit()
            
            bulk_insert_time = time.time() - start_time
            
            # 測試批量查詢性能
            start_time = time.time()
            
            from app.infrastructure.repositories.subscription_repository import SubscriptionRepository
            repo = SubscriptionRepository(db_session)
            
            all_subscriptions = repo.get_by_user_id(test_user.id)
            bulk_query_time = time.time() - start_time
            
            # 測試批量更新性能
            start_time = time.time()
            
            for subscription in subscriptions[:50]:  # 更新前50個
                subscription.price = subscription.price * 1.1
            
            db_session.commit()
            bulk_update_time = time.time() - start_time
            
            print(f"\n批量操作性能:")
            print(f"批量插入 {bulk_size} 條記錄: {bulk_insert_time:.4f}s")
            print(f"批量查詢 {len(all_subscriptions)} 條記錄: {bulk_query_time:.4f}s")
            print(f"批量更新 50 條記錄: {bulk_update_time:.4f}s")
            
            # 性能基準
            assert bulk_insert_time < 5.0, f"批量插入過慢: {bulk_insert_time:.4f}s"
            assert bulk_query_time < 2.0, f"批量查詢過慢: {bulk_query_time:.4f}s"
            assert bulk_update_time < 2.0, f"批量更新過慢: {bulk_update_time:.4f}s"

    @pytest.mark.performance
    @pytest.mark.slow
    class TestBusinessLogicPerformance:
        """業務邏輯性能測試"""

        def test_domain_service_performance(self, test_user, db_session):
            """測試領域服務性能"""
            from app.domain.services.subscription_domain_service import SubscriptionDomainService
            from app.infrastructure.services.exchange_rate_service_impl import ExchangeRateServiceImpl
            from app.models.subscription import Subscription, SubscriptionCycle, SubscriptionCategory, Currency
            
            # 創建服務實例
            exchange_service = ExchangeRateServiceImpl()
            domain_service = SubscriptionDomainService(exchange_service)
            
            # 創建測試數據
            subscriptions = []
            for i in range(50):
                subscription = Subscription(
                    name=f"Performance Test {i}",
                    price=float(i + 1) * 10,
                    original_price=float(i + 1) * 10,
                    currency=Currency.TWD,
                    cycle=SubscriptionCycle.MONTHLY,
                    category=SubscriptionCategory.ENTERTAINMENT,
                    user_id=test_user.id,
                    start_date=datetime(2024, 1, 1),
                    is_active=True
                )
                subscriptions.append(subscription)
            
            # 測試計算性能
            start_time = time.time()
            
            # 計算總成本
            total_monthly = domain_service.calculate_total_monthly_cost(subscriptions)
            total_yearly = domain_service.calculate_total_yearly_cost(subscriptions)
            
            # 按類別分組
            grouped = domain_service.group_by_category(subscriptions)
            
            # 計算類別成本
            category_costs = domain_service.calculate_category_costs(subscriptions)
            
            calculation_time = time.time() - start_time
            
            print(f"\n領域服務性能 (50個訂閱):")
            print(f"計算時間: {calculation_time:.4f}s")
            print(f"月度總成本: {total_monthly}")
            print(f"年度總成本: {total_yearly}")
            print(f"類別數量: {len(grouped)}")
            print(f"類別成本項目: {len(category_costs)}")
            
            # 計算時間應該很快
            assert calculation_time < 0.1, f"領域服務計算過慢: {calculation_time:.4f}s"

        def test_application_service_performance(self, test_user, db_session):
            """測試應用服務性能"""
            from app.application.services.subscription_application_service import SubscriptionApplicationService
            from app.domain.services.subscription_domain_service import SubscriptionDomainService
            from app.infrastructure.services.exchange_rate_service_impl import ExchangeRateServiceImpl
            from app.infrastructure.unit_of_work import SQLAlchemyUnitOfWork
            from app.application.dtos.subscription_dtos import SubscriptionQuery
            
            # 創建服務實例
            exchange_service = ExchangeRateServiceImpl()
            domain_service = SubscriptionDomainService(exchange_service)
            uow = SQLAlchemyUnitOfWork(db_session)
            app_service = SubscriptionApplicationService(uow, domain_service)
            
            # 創建一些測試數據
            from app.models.subscription import Subscription, SubscriptionCycle, SubscriptionCategory, Currency
            
            for i in range(20):
                subscription = Subscription(
                    name=f"App Service Test {i}",
                    price=100.0,
                    original_price=100.0,
                    currency=Currency.TWD,
                    cycle=SubscriptionCycle.MONTHLY,
                    category=SubscriptionCategory.ENTERTAINMENT,
                    user_id=test_user.id,
                    start_date=datetime(2024, 1, 1),
                    is_active=True
                )
                db_session.add(subscription)
            
            db_session.commit()
            
            # 測試應用服務性能
            start_time = time.time()
            
            # 獲取訂閱列表
            query = SubscriptionQuery(user_id=test_user.id)
            subscriptions = app_service.get_subscriptions(query)
            
            # 獲取摘要
            summary = app_service.get_subscription_summary(test_user.id)
            
            service_time = time.time() - start_time
            
            print(f"\n應用服務性能:")
            print(f"服務調用時間: {service_time:.4f}s")
            print(f"返回訂閱數量: {len(subscriptions)}")
            print(f"摘要 - 總訂閱: {summary.total_subscriptions}")
            print(f"摘要 - 活躍訂閱: {summary.active_subscriptions}")
            
            # 應用服務調用應該快速
            assert service_time < 1.0, f"應用服務調用過慢: {service_time:.4f}s"

    @pytest.mark.performance
    class TestLoadTesting:
        """負載測試"""

        def test_sustained_load(self, new_client, auth_headers):
            """測試持續負載"""
            duration = 30  # 30秒測試
            request_count = 0
            error_count = 0
            response_times = []
            
            start_time = time.time()
            
            while time.time() - start_time < duration:
                request_start = time.time()
                
                try:
                    response = new_client.get("/api/v1/subscriptions/", headers=auth_headers)
                    request_end = time.time()
                    
                    request_count += 1
                    response_times.append(request_end - request_start)
                    
                    if response.status_code >= 400:
                        error_count += 1
                        
                except Exception as e:
                    error_count += 1
                    print(f"請求異常: {e}")
                
                time.sleep(0.1)  # 100ms 間隔
            
            # 分析結果
            total_time = time.time() - start_time
            requests_per_second = request_count / total_time
            error_rate = error_count / request_count * 100 if request_count > 0 else 0
            avg_response_time = mean(response_times) if response_times else 0
            
            print(f"\n持續負載測試結果 ({duration}秒):")
            print(f"總請求數: {request_count}")
            print(f"錯誤數: {error_count}")
            print(f"錯誤率: {error_rate:.2f}%")
            print(f"每秒請求數: {requests_per_second:.2f}")
            print(f"平均響應時間: {avg_response_time:.4f}s")
            
            # 性能基準
            assert requests_per_second >= 5, f"每秒請求數過低: {requests_per_second:.2f}"
            assert error_rate < 5, f"錯誤率過高: {error_rate:.2f}%"
            assert avg_response_time < 2.0, f"平均響應時間過長: {avg_response_time:.4f}s"

        def test_spike_load(self, new_client, auth_headers):
            """測試突發負載"""
            spike_requests = 20
            results = []
            
            # 並發發送大量請求
            def make_request():
                start_time = time.time()
                try:
                    response = new_client.get("/api/v1/subscriptions/", headers=auth_headers)
                    end_time = time.time()
                    return {
                        'response_time': end_time - start_time,
                        'status_code': response.status_code,
                        'success': response.status_code < 400
                    }
                except Exception as e:
                    return {
                        'response_time': None,
                        'status_code': None,
                        'success': False,
                        'error': str(e)
                    }
            
            # 使用線程池並發執行
            with ThreadPoolExecutor(max_workers=spike_requests) as executor:
                futures = [executor.submit(make_request) for _ in range(spike_requests)]
                
                for future in as_completed(futures):
                    results.append(future.result())
            
            # 分析突發負載結果
            successful_requests = [r for r in results if r['success']]
            failed_requests = [r for r in results if not r['success']]
            
            success_rate = len(successful_requests) / len(results) * 100
            avg_response_time = mean([r['response_time'] for r in successful_requests]) if successful_requests else 0
            
            print(f"\n突發負載測試結果 ({spike_requests} 並發請求):")
            print(f"成功請求: {len(successful_requests)}")
            print(f"失敗請求: {len(failed_requests)}")
            print(f"成功率: {success_rate:.2f}%")
            print(f"平均響應時間: {avg_response_time:.4f}s")
            
            # 突發負載基準
            assert success_rate >= 80, f"突發負載成功率過低: {success_rate:.2f}%"
            assert avg_response_time < 5.0, f"突發負載響應時間過長: {avg_response_time:.4f}s"