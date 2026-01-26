#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 Google 整合記錄功能
"""

import sys
import os
from pathlib import Path

# 添加模組路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.file_manager import SmartFileManager

def test_google_integration_logging():
    """測試 Google 整合記錄功能"""
    print("測試 Google 整合記錄功能")
    print("=" * 50)

    # 建立文件管理器
    file_manager = SmartFileManager()

    # 模擬分析結果
    mock_analysis = {
        'refined_subject': '測試公文主旨',
        'document_type': '通知',
        'priority': '中',
        'key_points': ['重要事項1', '重要事項2'],
        'action_items': [
            {'description': '填寫表單', 'deadline': '2024-12-31', 'priority': '高'}
        ],
        'important_dates': [
            {'date': '2024-12-15', 'description': '截止日期'}
        ],
        'contact_info': {
            'name': '承辦人姓名',
            'phone': '02-12345678',
            'email': 'test@example.com'
        },
        'suggested_filename': '2024-12-15_測試公文主旨'
    }

    # 模擬文件資訊
    mock_doc_info = {
        'file_name': 'test_print.pdf',
        'dates': [{'year': 113, 'month': 12, 'day': 15}],
        'attachments': []
    }

    # 模擬 Google 整合結果 - 成功的行事曆事件
    mock_google_result_calendar = {
        'success': True,
        'type': 'calendar',
        'id': 'test-event-id',
        'title': '測試公文主旨',
        'date': '2024-12-15 09:00',
        'url': 'https://calendar.google.com/event?eid=test-event-id'
    }

    # 模擬 Google 整合結果 - 成功的任務
    mock_google_result_task = {
        'success': True,
        'type': 'task',
        'id': 'test-task-id',
        'title': '測試公文主旨',
        'due_date': '2024-12-31',
        'url': 'https://tasks.google.com/embed/list/test-task-id'
    }

    # 模擬 Google 整合結果 - 失敗
    mock_google_result_failed = {
        'success': False,
        'type': 'calendar',
        'error': '無法連接到 Google Calendar API'
    }

    # 創建測試檔案
    test_file = Path("test_document.pdf")
    test_file.touch(exist_ok=True)

    try:
        print("\\n1. 測試包含成功的行事曆事件記錄...")
        result1 = file_manager.organize_document(
            source_file=str(test_file),
            doc_info=mock_doc_info,
            analysis=mock_analysis,
            google_result=mock_google_result_calendar
        )

        if result1['success']:
            print(f"   [成功] {result1['target_path']}")

            # 檢查處理記錄是否包含 Google 整合結果
            log_file = Path(result1['target_path']) / "處理記錄.txt"
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_content = f.read()
                    if 'Google 整合記錄:' in log_content and 'calendar' in log_content:
                        print(f"   [OK] 處理記錄包含行事曆整合資訊")
                    else:
                        print(f"   [NG] 處理記錄缺少行事曆整合資訊")
            else:
                print(f"   [NG] 處理記錄檔案不存在")
        else:
            print(f"   [失敗] {result1['error']}")

        print("\\n2. 測試包含成功的任務記錄...")
        result2 = file_manager.organize_document(
            source_file=str(test_file),
            doc_info=mock_doc_info,
            analysis=mock_analysis,
            google_result=mock_google_result_task
        )

        if result2['success']:
            print(f"   [成功] {result2['target_path']}")

            # 檢查處理記錄是否包含 Google 整合結果
            log_file = Path(result2['target_path']) / "處理記錄.txt"
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_content = f.read()
                    if 'Google 整合記錄:' in log_content and 'task' in log_content:
                        print(f"   [OK] 處理記錄包含任務整合資訊")
                    else:
                        print(f"   [NG] 處理記錄缺少任務整合資訊")
            else:
                print(f"   [NG] 處理記錄檔案不存在")

        print("\\n3. 測試包含失敗的 Google 整合記錄...")
        result3 = file_manager.organize_document(
            source_file=str(test_file),
            doc_info=mock_doc_info,
            analysis=mock_analysis,
            google_result=mock_google_result_failed
        )

        if result3['success']:
            print(f"   [成功] {result3['target_path']}")

            # 檢查處理記錄是否包含失敗的 Google 整合結果
            log_file = Path(result3['target_path']) / "處理記錄.txt"
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_content = f.read()
                    if 'Google 整合記錄:' in log_content and '失敗' in log_content:
                        print(f"   [OK] 處理記錄包含失敗的整合資訊")
                    else:
                        print(f"   [NG] 處理記錄缺少失敗的整合資訊")
            else:
                print(f"   [NG] 處理記錄檔案不存在")

        print("\\n4. 測試沒有 Google 整合的情況...")
        result4 = file_manager.organize_document(
            source_file=str(test_file),
            doc_info=mock_doc_info,
            analysis=mock_analysis,
            google_result=None
        )

        if result4['success']:
            print(f"   [成功] {result4['target_path']}")

            # 檢查處理記錄是否正確標示未執行
            log_file = Path(result4['target_path']) / "處理記錄.txt"
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_content = f.read()
                    if 'Google 整合記錄: 未執行' in log_content:
                        print(f"   [OK] 處理記錄正確標示未執行整合")
                    else:
                        print(f"   [NG] 處理記錄未正確標示未執行整合")
            else:
                print(f"   [NG] 處理記錄檔案不存在")

        print("\\n5. 測試覆蓋行為...")
        # 再次處理同一份文件，確認覆蓋功能
        result5 = file_manager.organize_document(
            source_file=str(test_file),
            doc_info=mock_doc_info,
            analysis=mock_analysis,
            google_result=mock_google_result_calendar
        )

        if result5['success']:
            print(f"   [OK] 覆蓋測試成功: {result5['target_path']}")
        else:
            print(f"   [NG] 覆蓋測試失敗: {result5['error']}")

    except Exception as e:
        print(f"測試過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 清理測試檔案
        if test_file.exists():
            test_file.unlink()

    print("\\n測試完成！")

if __name__ == "__main__":
    test_google_integration_logging()