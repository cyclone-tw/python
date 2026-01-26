#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化測試 - 只測試核心功能
"""

import sys
import os
from pathlib import Path

# 添加模組路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from modules.file_manager import SmartFileManager

    # 建立文件管理器
    file_manager = SmartFileManager()

    # 模擬簡單的 Google 結果
    google_result = {
        'success': True,
        'type': 'calendar',
        'title': 'Test Event',
        'date': '2024-12-15',
        'url': 'https://calendar.google.com/test'
    }

    # 模擬分析結果
    analysis = {
        'suggested_filename': '2024-12-15_minimal_test',
        'refined_subject': 'Minimal Test'
    }

    # 模擬文件資訊
    doc_info = {
        'file_name': 'test.pdf',
        'dates': [],
        'attachments': []
    }

    # 創建測試檔案
    test_file = Path("minimal_test.pdf")
    test_file.touch(exist_ok=True)

    try:
        # 測試核心功能
        result = file_manager.organize_document(
            source_file=str(test_file),
            doc_info=doc_info,
            analysis=analysis,
            google_result=google_result
        )

        if result['success']:
            print("SUCCESS: Document organized successfully")
            print(f"Target path: {result['target_path']}")

            # 檢查處理記錄
            log_file = Path(result['target_path']) / "處理記錄.txt"
            if log_file.exists():
                print("SUCCESS: Processing log created")
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'Google 整合記錄:' in content:
                        print("SUCCESS: Google integration info included in log")
                    else:
                        print("ERROR: Google integration info missing from log")
            else:
                print("ERROR: Processing log not created")
        else:
            print(f"ERROR: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 清理
        if test_file.exists():
            test_file.unlink()

except ImportError as e:
    print(f"Import Error: {e}")
except Exception as e:
    print(f"General Error: {e}")