#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試修復後的 Gemini API
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 設定編碼以支援中文輸出
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except:
    pass

from modules.gemini_analyzer import GeminiSmartAnalyzer

def test_gemini():
    print("=== 測試 Gemini API 修復 ===")

    # 初始化分析器
    analyzer = GeminiSmartAnalyzer()

    if not analyzer.is_available:
        print("❌ Gemini API 無法使用")
        return False

    print("✅ Gemini API 初始化成功")

    # 測試簡單調用
    test_doc = {
        'file_name': 'test.pdf',
        'sections': {
            '主旨': '測試公文分析功能'
        },
        'dates': ['2024-12-15'],
        'metadata': {
            '發文機關': '測試機關'
        }
    }

    try:
        print("🤖 測試文件分析...")
        result = analyzer.analyze_document(test_doc)

        if 'error' in result:
            print(f"❌ 分析失敗: {result['error']}")
            return False
        else:
            print("✅ 分析成功!")
            print(f"   - 文件類型: {result.get('document_type', 'N/A')}")
            print(f"   - 重要性: {result.get('priority', 'N/A')}")
            return True

    except Exception as e:
        print(f"❌ 測試過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_gemini()
    print(f"\n=== 測試結果: {'成功' if success else '失敗'} ===")