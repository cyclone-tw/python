#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""快速測試 Gemini API"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from modules.gemini_analyzer import GeminiSmartAnalyzer

# 測試數據
test_doc = {
    'file_name': 'test.pdf',
    'metadata': {
        '主旨': '測試公文',
        '發文日期': '113年12月8日'
    },
    'sections': {
        '主旨': '轉知教育部辦理教師研習活動，請各校踴躍參加。',
        '說明': '一、依據教育部113年12月1日函辦理。\n二、研習時間：113年12月15日（星期五）。'
    },
    'dates': [
        {'year': 113, 'month': 12, 'day': 15, 'raw': '113年12月15日', 'type': 'date'}
    ],
    'attachments': []
}

print("=" * 50)
print("🧪 開始測試 Gemini API")
print("=" * 50)

analyzer = GeminiSmartAnalyzer()

if not analyzer.is_available:
    print("❌ Gemini API 無法使用")
    sys.exit(1)

print("\n🤖 開始分析測試文件...")
result = analyzer.analyze_document(test_doc)

if 'error' in result:
    print(f"\n❌ 分析失敗: {result['error']}")
    sys.exit(1)

print("\n✅ 分析成功！")
print("=" * 50)
print(f"📝 建議檔名: {result.get('suggested_filename', '未知')}")
print(f"📋 精簡主旨: {result.get('refined_subject', '未知')}")
print(f"🗂️  文件類型: {result.get('document_type', '未知')}")
print(f"⚡ 重要性: {result.get('priority', '未知')}")
print(f"📅 重要日期數量: {len(result.get('important_dates', []))}")
print(f"📝 行動項目數量: {len(result.get('action_items', []))}")
print("=" * 50)
print("\n🎉 測試完成！系統運作正常。")
