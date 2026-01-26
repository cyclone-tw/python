#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公文智能處理系統測試腳本
用於驗證各模組功能
"""

import sys
import os
from pathlib import Path

# 加入模組路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.document_processor import DocumentProcessor
from modules.gemini_analyzer import GeminiSmartAnalyzer
from modules.file_manager import SmartFileManager
from modules.google_integration import GoogleIntegration
from config import SETTINGS


def test_all_modules():
    """測試所有模組"""
    print("🧪 公文智能處理系統 - 模組測試")
    print("=" * 50)

    # 1. 測試 PDF 處理器
    print("\n1️⃣ 測試 DocumentProcessor...")
    processor = DocumentProcessor()
    print("   ✅ DocumentProcessor 初始化成功")

    # 2. 測試 Gemini 分析器
    print("\n2️⃣ 測試 GeminiSmartAnalyzer...")
    analyzer = GeminiSmartAnalyzer()
    if analyzer.is_available:
        print("   ✅ GeminiSmartAnalyzer 初始化成功")
    else:
        print("   ❌ GeminiSmartAnalyzer 初始化失敗 - 請檢查 API Key")

    # 3. 測試檔案管理器
    print("\n3️⃣ 測試 SmartFileManager...")
    file_manager = SmartFileManager()
    print(f"   ✅ SmartFileManager 初始化成功")
    print(f"   目標目錄: {file_manager.target_base}")

    # 4. 測試 Google 整合
    print("\n4️⃣ 測試 GoogleIntegration...")
    google_integration = GoogleIntegration()
    if google_integration.is_authenticated:
        print("   ✅ GoogleIntegration 認證成功")
    else:
        print("   ❌ GoogleIntegration 認證失敗")

    # 5. 檢查掃描目錄
    print("\n5️⃣ 檢查設定...")
    scan_path = Path(SETTINGS['paths']['scan_directory'])
    target_path = Path(SETTINGS['paths']['target_directory'])

    print(f"   掃描目錄: {scan_path}")
    print(f"   是否存在: {'✅' if scan_path.exists() else '❌'}")

    print(f"   目標目錄: {target_path}")
    print(f"   是否存在: {'✅' if target_path.exists() else '❌'}")

    # 6. 尋找測試檔案
    print("\n6️⃣ 尋找 _print.pdf 檔案...")
    if scan_path.exists():
        pdf_files = list(scan_path.glob("*_print.pdf"))
        print(f"   找到 {len(pdf_files)} 個 _print.pdf 檔案")
        for pdf_file in pdf_files[:5]:  # 最多顯示5個
            print(f"     - {pdf_file.name}")
        if len(pdf_files) > 5:
            print(f"     ... 還有 {len(pdf_files) - 5} 個檔案")
    else:
        print("   ❌ 掃描目錄不存在")

    print("\n" + "=" * 50)
    print("🎯 測試完成！如果看到任何 ❌，請檢查相關設定。")


def test_single_file(pdf_path: str):
    """測試單一檔案處理"""
    if not pdf_path.endswith('_print.pdf'):
        print("❌ 檔案名稱必須以 _print.pdf 結尾")
        return

    if not os.path.exists(pdf_path):
        print(f"❌ 檔案不存在: {pdf_path}")
        return

    print(f"🧪 測試單一檔案: {os.path.basename(pdf_path)}")
    print("=" * 50)

    # 初始化模組
    processor = DocumentProcessor()
    analyzer = GeminiSmartAnalyzer()

    # 1. 處理PDF
    print("\n1️⃣ 處理PDF...")
    doc_info = processor.process_pdf(pdf_path)
    if not doc_info:
        print("❌ PDF處理失敗")
        return

    print(f"   ✅ PDF處理成功")
    print(f"   文字長度: {len(doc_info.get('full_text', ''))}")
    print(f"   段落數: {len(doc_info.get('sections', {}))}")
    print(f"   日期數: {len(doc_info.get('dates', []))}")
    print(f"   附件數: {len(doc_info.get('attachments', []))}")

    # 2. Gemini分析
    if analyzer.is_available:
        print("\n2️⃣ Gemini分析...")
        analysis = analyzer.analyze_document(doc_info)
        if 'error' in analysis:
            print(f"❌ 分析失敗: {analysis['error']}")
        else:
            print("   ✅ 分析成功")
            print(f"   主旨: {analysis.get('refined_subject', '')}")
            print(f"   建議檔名: {analysis.get('suggested_filename', '')}")
            print(f"   建議路徑: {analysis.get('suggested_path', '')}")
    else:
        print("\n2️⃣ 跳過Gemini分析（API未設定）")

    print("\n" + "=" * 50)
    print("🎯 單一檔案測試完成！")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 測試單一檔案
        test_single_file(sys.argv[1])
    else:
        # 測試所有模組
        test_all_modules()