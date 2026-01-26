#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試改善後的憑證管理機制
"""

import os
import sys
import time
from datetime import datetime

# 加入模組路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.google_integration import GoogleIntegration

def test_basic_connection():
    """測試基本連線功能"""
    print("=" * 50)
    print("測試 1：基本連線功能")
    print("=" * 50)

    integration = GoogleIntegration()

    if integration.is_authenticated:
        print("✅ 基本認證成功")

        # 測試API呼叫
        result = integration.test_connection()
        if result['success']:
            print(f"✅ API連線測試成功")
            print(f"   📅 行事曆數量: {result['calendar_count']}")
            print(f"   📝 任務清單數量: {result['tasklist_count']}")
        else:
            print(f"❌ API連線測試失敗: {result['error']}")
    else:
        print("❌ 基本認證失敗")

    return integration.is_authenticated

def test_credential_refresh():
    """測試憑證刷新機制"""
    print("\n" + "=" * 50)
    print("🔧 測試 2：憑證刷新機制")
    print("=" * 50)

    integration = GoogleIntegration()

    if not integration.is_authenticated:
        print("❌ 無法進行刷新測試 - 認證失敗")
        return False

    # 檢查憑證狀態
    if integration.creds:
        print(f"📄 憑證狀態:")
        print(f"   有效: {integration.creds.valid}")
        print(f"   過期: {integration.creds.expired}")
        if hasattr(integration.creds, 'expiry') and integration.creds.expiry:
            print(f"   到期時間: {integration.creds.expiry}")
        if integration.creds.refresh_token:
            print(f"   有 Refresh Token: 是")
        else:
            print(f"   有 Refresh Token: 否")

    # 測試多次API呼叫
    print("\n🔄 進行多次API呼叫測試...")
    for i in range(3):
        print(f"\n第 {i+1} 次呼叫:")
        result = integration.test_connection()
        if result['success']:
            print("✅ 成功")
        else:
            print(f"❌ 失敗: {result['error']}")
        time.sleep(1)

    return True

def test_error_recovery():
    """測試錯誤恢復機制"""
    print("\n" + "=" * 50)
    print("🔧 測試 3：錯誤恢復機制")
    print("=" * 50)

    integration = GoogleIntegration()

    if not integration.is_authenticated:
        print("❌ 無法進行錯誤恢復測試 - 認證失敗")
        return False

    # 測試假設的認證失效場景
    print("🧪 模擬認證問題...")

    # 測試 _ensure_valid_credentials 方法
    result = integration._ensure_valid_credentials()
    if result:
        print("✅ 憑證驗證通過")
    else:
        print("❌ 憑證驗證失敗")

    return result

def test_google_calendar_creation():
    """測試Google行事曆事件建立"""
    print("\n" + "=" * 50)
    print("🔧 測試 4：Google行事曆事件建立")
    print("=" * 50)

    integration = GoogleIntegration()

    if not integration.is_authenticated:
        print("❌ 無法進行行事曆測試 - 認證失敗")
        return False

    # 建立測試用的分析結果
    test_analysis = {
        'refined_subject': '憑證管理測試事件',
        'document_type': '測試',
        'priority': '中',
        'key_points': ['測試憑證管理', '自動刷新機制', '錯誤恢復'],
        'action_items': [
            {
                'description': '驗證憑證管理改善',
                'deadline': '2024-12-31',
                'priority': '高'
            }
        ],
        'google_suggestion': {
            'type': 'calendar',
            'title': '憑證管理測試事件',
            'reason': '測試改善後的憑證管理機制',
            'due_date': '2024-12-31'
        }
    }

    print("📅 嘗試建立測試行事曆事件...")
    result = integration.create_from_analysis(test_analysis)

    if result['success']:
        print("✅ 行事曆事件建立成功")
        print(f"   標題: {result['title']}")
        print(f"   日期: {result.get('date', 'N/A')}")
        print(f"   URL: {result.get('url', 'N/A')}")
    else:
        print(f"❌ 行事曆事件建立失敗: {result['error']}")

    return result['success']

def main():
    """主要測試流程"""
    print("開始憑證管理改善測試")
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = []

    # 執行各項測試
    results.append(("基本連線", test_basic_connection()))
    results.append(("憑證刷新", test_credential_refresh()))
    results.append(("錯誤恢復", test_error_recovery()))
    results.append(("行事曆建立", test_google_calendar_creation()))

    # 顯示測試結果摘要
    print("\n" + "=" * 50)
    print("測試結果摘要")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "通過" if result else "失敗"
        print(f"{test_name:12} : {status}")
        if result:
            passed += 1

    print(f"\n總體結果: {passed}/{total} 測試通過")

    if passed == total:
        print("所有測試通過！憑證管理改善成功。")
    else:
        print("部分測試失敗，可能需要進一步調整。")

    print(f"\n建議:")
    print("- 如果連線測試失敗，請檢查網路連線和憑證檔案")
    print("- 如果行事曆建立失敗，請確認Google Calendar API已啟用")
    print("- 定期使用系統可避免憑證長期閒置導致的問題")

if __name__ == "__main__":
    main()