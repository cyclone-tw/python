#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試附件匹配修復
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

from modules.document_processor import DocumentProcessor
from pathlib import Path

def test_attachment_matching():
    """測試附件匹配邏輯"""
    print("=== 測試附件匹配修復 ===\n")

    processor = DocumentProcessor()

    # 測試案例：模擬你的三個公文檔案
    test_cases = [
        "376480000A_1140221864_print.pdf",
        "376480000A_1140221050_print.pdf",
        "376480000A_1140223153_print.pdf"
    ]

    # 測試每個檔案的附件匹配
    for pdf_name in test_cases:
        print(f"📄 測試檔案: {pdf_name}")

        # 模擬完整路徑（使用實際掃描目錄）
        from config import SETTINGS
        scan_dir = Path(SETTINGS['paths']['scan_directory'])
        full_path = str(scan_dir / pdf_name)

        try:
            # 測試附件匹配
            attachments = processor._find_attachments_by_prefix(full_path)

            print(f"   📎 找到 {len(attachments)} 個附件")
            for att in attachments:
                print(f"      - {att['filename']}")

        except Exception as e:
            print(f"   ❌ 測試失敗: {e}")

        print()

    print("=== 測試完成 ===")

def test_regex_matching():
    """測試正規表達式匹配"""
    print("\n=== 測試正規表達式匹配 ===")

    import re

    test_files = [
        "376480000A_1140221864_print.pdf",
        "376480000A_1140221050_print.pdf",
        "376480000A_1140223153_print.pdf",
        "376480000A_1140221864_ATTACH1.pdf",
        "376480000A_1140223153_ATTACH1.pdf",
        "376480000A_1140223153_ATTACH2.pdf"
    ]

    for filename in test_files:
        match = re.match(r'^([A-Za-z0-9]+_[0-9]+)_print\.pdf$', filename)
        if match:
            document_id = match.group(1)
            print(f"✅ {filename} -> 文件編號: {document_id}")
        else:
            print(f"⚪ {filename} -> 不是主文件")

    print("\n附件匹配測試:")
    main_doc_id = "376480000A_1140221864"

    for filename in test_files:
        if filename.startswith(f"{main_doc_id}_ATTACH"):
            print(f"✅ {filename} -> 屬於 {main_doc_id}")
        elif filename.startswith(f"{main_doc_id}_print"):
            print(f"📄 {filename} -> 主文件")
        else:
            print(f"❌ {filename} -> 不屬於 {main_doc_id}")

if __name__ == "__main__":
    test_regex_matching()
    test_attachment_matching()