#!/bin/bash

# 測試執行腳本
echo "🚀 開始執行前端重構測試套件"
echo "=================================="

# 檢查 Node.js 和 npm
if ! command -v node &> /dev/null; then
    echo "❌ 錯誤: 需要安裝 Node.js"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ 錯誤: 需要安裝 npm"
    exit 1
fi

# 進入測試目錄
cd "$(dirname "$0")"

# 安裝依賴
echo "📦 安裝測試依賴..."
npm install

# 建立測試結果目錄
mkdir -p results

# 執行單元測試
echo ""
echo "🧪 執行單元測試..."
echo "=================="
npm test -- --coverage --coverageDirectory=results/coverage > results/unit-test-results.txt 2>&1
UNIT_EXIT_CODE=$?

if [ $UNIT_EXIT_CODE -eq 0 ]; then
    echo "✅ 單元測試通過"
else
    echo "❌ 單元測試失敗"
fi

# 執行集成測試
echo ""
echo "🔗 執行集成測試..."
echo "=================="
npm test -- --testMatch="**/integration/**/*.test.js" > results/integration-test-results.txt 2>&1
INTEGRATION_EXIT_CODE=$?

if [ $INTEGRATION_EXIT_CODE -eq 0 ]; then
    echo "✅ 集成測試通過"
else
    echo "❌ 集成測試失敗"
fi

# 啟動本地服務器進行 E2E 測試
echo ""
echo "🌐 啟動本地服務器..."
npm run serve &
SERVER_PID=$!

# 等待服務器啟動
sleep 5

# 檢查服務器是否正常運行
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ 服務器啟動成功"
    
    # 執行 E2E 測試
    echo ""
    echo "🎭 執行 E2E 測試..."
    echo "=================="
    npm run test:e2e > results/e2e-test-results.txt 2>&1
    E2E_EXIT_CODE=$?
    
    if [ $E2E_EXIT_CODE -eq 0 ]; then
        echo "✅ E2E 測試通過"
    else
        echo "❌ E2E 測試失敗"
    fi
else
    echo "❌ 服務器啟動失敗"
    E2E_EXIT_CODE=1
fi

# 關閉服務器
kill $SERVER_PID 2>/dev/null

# 生成測試報告
echo ""
echo "📊 生成測試報告..."
echo "=================="

# 創建 HTML 測試報告
cat > results/test-report.html << 'EOF'
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>前端重構測試報告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f5f5f5; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .pass { color: #28a745; }
        .fail { color: #dc3545; }
        .warning { color: #ffc107; }
        .info { color: #17a2b8; }
        pre { background: #f8f9fa; padding: 10px; border-radius: 4px; overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📋 前端重構測試報告</h1>
        <p><strong>測試時間:</strong> $(date)</p>
        <p><strong>測試環境:</strong> Node.js $(node --version), npm $(npm --version)</p>
    </div>
    
    <div class="section">
        <h2>📊 測試總覽</h2>
        <table>
            <tr><th>測試類型</th><th>狀態</th><th>描述</th></tr>
            <tr><td>單元測試</td><td class="$([ $UNIT_EXIT_CODE -eq 0 ] && echo 'pass' || echo 'fail')">$([ $UNIT_EXIT_CODE -eq 0 ] && echo '✅ 通過' || echo '❌ 失敗')</td><td>測試個別組件和函數</td></tr>
            <tr><td>集成測試</td><td class="$([ $INTEGRATION_EXIT_CODE -eq 0 ] && echo 'pass' || echo 'fail')">$([ $INTEGRATION_EXIT_CODE -eq 0 ] && echo '✅ 通過' || echo '❌ 失敗')</td><td>測試組件間協作</td></tr>
            <tr><td>E2E 測試</td><td class="$([ $E2E_EXIT_CODE -eq 0 ] && echo 'pass' || echo 'fail')">$([ $E2E_EXIT_CODE -eq 0 ] && echo '✅ 通過' || echo '❌ 失敗')</td><td>測試完整用戶流程</td></tr>
        </table>
    </div>
</body>
</html>
EOF

echo "✅ 測試報告已生成: results/test-report.html"

# 輸出總結
echo ""
echo "🎯 測試總結"
echo "==========="
echo "單元測試: $([ $UNIT_EXIT_CODE -eq 0 ] && echo '✅ 通過' || echo '❌ 失敗')"
echo "集成測試: $([ $INTEGRATION_EXIT_CODE -eq 0 ] && echo '✅ 通過' || echo '❌ 失敗')" 
echo "E2E 測試: $([ $E2E_EXIT_CODE -eq 0 ] && echo '✅ 通過' || echo '❌ 失敗')"

# 整體結果
OVERALL_EXIT_CODE=0
if [ $UNIT_EXIT_CODE -ne 0 ] || [ $INTEGRATION_EXIT_CODE -ne 0 ] || [ $E2E_EXIT_CODE -ne 0 ]; then
    OVERALL_EXIT_CODE=1
    echo ""
    echo "❌ 部分測試失敗，請檢查測試結果文件獲取詳細信息"
else
    echo ""
    echo "🎉 所有測試通過！重構成功！"
fi

echo ""
echo "📁 測試結果文件:"
echo "  - results/unit-test-results.txt"
echo "  - results/integration-test-results.txt" 
echo "  - results/e2e-test-results.txt"
echo "  - results/coverage/ (測試覆蓋率報告)"
echo "  - results/test-report.html (HTML 報告)"

exit $OVERALL_EXIT_CODE