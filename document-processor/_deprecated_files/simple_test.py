#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化版憑證管理測試
"""

import os
import sys

# 加入模組路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.google_integration import GoogleIntegration

def main():
    print("=" * 40)
    print("測試改善後的憑證管理")
    print("=" * 40)

    try:
        # 建立Google整合實例
        integration = GoogleIntegration()

        if integration.is_authenticated:
            print("認證成功!")

            # 測試連線
            print("測試API連線...")
            result = integration.test_connection()

            if result['success']:
                print("API連線成功!")
                print(f"行事曆數量: {result['calendar_count']}")
                print(f"任務清單數量: {result['tasklist_count']}")
            else:
                print(f"API連線失敗: {result['error']}")

        else:
            print("認證失敗")

    except Exception as e:
        print(f"測試過程發生錯誤: {e}")

    print("=" * 40)
    print("測試完成")

if __name__ == "__main__":
    main()