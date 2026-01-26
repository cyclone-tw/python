#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公文處理器 - PDF內容提取與結構化
基於原有 pdf_processor.py 優化，專注於內容提取
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️ pdfplumber 未安裝，請執行: pip install pdfplumber")

from config import SETTINGS


class DocumentProcessor:
    """公文處理器"""

    def __init__(self):
        self.noise_patterns = SETTINGS['pdf_processing']['noise_patterns']
        self.section_patterns = SETTINGS['pdf_processing']['section_patterns']

    def process_pdf(self, pdf_path: str) -> Optional[Dict]:
        """處理PDF檔案，提取結構化內容"""
        if not PDF_AVAILABLE:
            print("❌ pdfplumber 套件未安裝")
            return None

        if not os.path.exists(pdf_path):
            print(f"❌ 檔案不存在: {pdf_path}")
            return None

        try:
            print(f"🔍 正在處理PDF: {os.path.basename(pdf_path)}")

            with pdfplumber.open(pdf_path) as pdf:
                # 提取所有文字
                full_text = ""
                page_count = len(pdf.pages)
                print(f"   PDF共有 {page_count} 頁")

                for i, page in enumerate(pdf.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            full_text += page_text + "\n"
                        print(f"   已處理第 {i}/{page_count} 頁")
                    except Exception as e:
                        print(f"   ⚠️ 第 {i} 頁處理失敗: {e}")
                        continue

                if not full_text.strip():
                    print(f"⚠️ PDF無內容或無法提取文字: {pdf_path}")
                    return {
                        'file_path': pdf_path,
                        'file_name': os.path.basename(pdf_path),
                        'full_text': '',
                        'sections': {'內容': '無法提取文字內容'},
                        'dates': [],
                        'attachments': self._find_attachments_by_prefix(pdf_path),
                        'metadata': {},
                        'processed_at': datetime.now().isoformat(),
                        'error': '無法提取PDF文字'
                    }

                print(f"   ✅ 成功提取文字，共 {len(full_text)} 字元")

                # 清理文字
                cleaned_text = self._clean_text(full_text)

                # 提取結構化內容
                sections = self._extract_sections(cleaned_text)
                dates = self._extract_dates(cleaned_text)
                attachments = self._find_attachments_by_prefix(pdf_path)

                print(f"   ✅ 找到 {len(sections)} 個段落，{len(dates)} 個日期，{len(attachments)} 個附件")

                # 建立文件資訊
                doc_info = {
                    'file_path': pdf_path,
                    'file_name': os.path.basename(pdf_path),
                    'full_text': cleaned_text,
                    'sections': sections,
                    'dates': dates,
                    'attachments': attachments,
                    'metadata': self._extract_metadata(sections),
                    'processed_at': datetime.now().isoformat()
                }

                return doc_info

        except Exception as e:
            print(f"❌ 處理PDF時發生錯誤: {e}")
            import traceback
            print(f"   詳細錯誤: {traceback.format_exc()}")
            return None

    def _clean_text(self, text: str) -> str:
        """清理文字，移除雜訊"""
        cleaned = text

        # 套用雜訊移除規則
        for pattern, replacement in self.noise_patterns:
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.MULTILINE)

        # 標準化空白字元
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = re.sub(r'\n\s*\n', '\n', cleaned)

        return cleaned.strip()

    def _extract_sections(self, text: str) -> Dict[str, str]:
        """提取公文各段落"""
        sections = {}

        # 分割文字為行
        lines = text.split('\n')
        current_section = None
        current_content = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 檢查是否為段落標題
            section_found = False
            for section_name, pattern in self.section_patterns.items():
                if re.search(pattern, line):
                    # 儲存前一個段落
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content).strip()

                    # 開始新段落
                    current_section = section_name
                    current_content = []

                    # 移除段落標題，保留內容
                    content = re.sub(pattern, '', line).strip()
                    if content:
                        current_content.append(content)

                    section_found = True
                    break

            # 如果不是段落標題，加入當前段落內容
            if not section_found and current_section:
                current_content.append(line)

        # 儲存最後一個段落
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content).strip()

        # 如果沒有識別到段落，將全文作為內容
        if not sections:
            sections['內容'] = text

        return sections

    def _extract_dates(self, text: str) -> List[Dict]:
        """提取日期資訊"""
        dates = []

        # 民國年格式
        roc_patterns = [
            r'(\d{2,3})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日',
            r'(\d{2,3})/(\d{1,2})/(\d{1,2})',
            r'(\d{2,3})-(\d{1,2})-(\d{1,2})'
        ]

        for pattern in roc_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                try:
                    year = int(match.group(1))
                    month = int(match.group(2))
                    day = int(match.group(3))

                    # 判斷日期類型
                    context = text[max(0, match.start()-20):match.end()+20]
                    date_type = self._classify_date_type(context)

                    dates.append({
                        'raw': match.group(0),
                        'year': year,
                        'month': month,
                        'day': day,
                        'type': date_type,
                        'context': context.strip()
                    })
                except ValueError:
                    continue

        # 西元年格式
        western_patterns = [
            r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日',
            r'(\d{4})/(\d{1,2})/(\d{1,2})',
            r'(\d{4})-(\d{1,2})-(\d{1,2})'
        ]

        for pattern in western_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                try:
                    year = int(match.group(1)) - 1911  # 轉為民國年
                    month = int(match.group(2))
                    day = int(match.group(3))

                    if year > 0:  # 確保是合理的民國年
                        context = text[max(0, match.start()-20):match.end()+20]
                        date_type = self._classify_date_type(context)

                        dates.append({
                            'raw': match.group(0),
                            'year': year,
                            'month': month,
                            'day': day,
                            'type': date_type,
                            'context': context.strip()
                        })
                except ValueError:
                    continue

        # 移除重複並排序
        unique_dates = []
        seen = set()
        for date in dates:
            key = (date['year'], date['month'], date['day'])
            if key not in seen:
                seen.add(key)
                unique_dates.append(date)

        return sorted(unique_dates, key=lambda x: (x['year'], x['month'], x['day']))

    def _classify_date_type(self, context: str) -> str:
        """判斷日期類型"""
        context_lower = context.lower()

        if any(word in context for word in ['截止', '繳交', '報名', '收件']):
            return 'deadline'
        elif any(word in context for word in ['舉辦', '辦理', '活動', '會議']):
            return 'event'
        elif any(word in context for word in ['發文', '來文']):
            return 'document'
        else:
            return 'general'

    def _extract_metadata(self, sections: Dict[str, str]) -> Dict[str, str]:
        """提取元數據"""
        metadata = {}

        # 提取發文字號
        for section_name, content in sections.items():
            if '字號' in section_name or '發文字號' in section_name:
                metadata['發文字號'] = content
                break

        # 提取發文日期
        for section_name, content in sections.items():
            if '日期' in section_name or '發文日期' in section_name:
                metadata['發文日期'] = content
                break

        # 提取受文者
        if '受文者' in sections:
            metadata['受文者'] = sections['受文者']

        return metadata

    def _find_attachments_by_prefix(self, pdf_path: str) -> List[Dict]:
        """根據完整文件編號尋找相關附件（修復版）"""
        attachments = []
        pdf_path_obj = Path(pdf_path)
        pdf_dir = pdf_path_obj.parent
        pdf_name = pdf_path_obj.name

        # 提取完整文件編號，例如從 "376480000A_1140221864_print.pdf" 提取 "376480000A_1140221864"
        import re
        match = re.match(r'^([A-Za-z0-9]+_[0-9]+)_print\.pdf$', pdf_name)
        if not match:
            # 嘗試簡單格式 "編號_print.pdf"
            match = re.match(r'^([A-Za-z0-9]+)_print\.pdf$', pdf_name)

        if not match:
            print(f"   ⚠️ 檔名格式不符合標準格式: {pdf_name}")
            return []

        document_id = match.group(1)  # 完整文件編號，如 "376480000A_1140221864"
        print(f"   🔍 尋找文件編號為 '{document_id}' 的附件...")

        # 在同目錄下尋找相同完整編號的附件檔案
        try:
            for file_path in pdf_dir.iterdir():
                if not file_path.is_file():
                    continue

                file_name = file_path.name

                # 跳過自己
                if file_name == pdf_name:
                    continue

                # 檢查是否為此文件的附件（必須是完整匹配文件編號）
                # 正確格式: 376480000A_1140221864_ATTACH1.pdf
                if (file_name.startswith(f"{document_id}_ATTACH") or
                    file_name.startswith(f"{document_id}.") or
                    (file_name.startswith(f"{document_id}_") and not file_name.endswith("_print.pdf"))):

                    attachments.append({
                        'filename': file_name,
                        'path': str(file_path),
                        'size': file_path.stat().st_size,
                        'type': file_path.suffix.lower(),
                        'document_id': document_id
                    })
                    print(f"     ✅ 找到附件: {file_name}")

        except Exception as e:
            print(f"   ⚠️ 搜尋附件時發生錯誤: {e}")

        print(f"   📎 共找到 {len(attachments)} 個附件")
        return attachments

    def _find_attachments(self, pdf_path: str) -> List[Dict]:
        """舊版附件尋找方法（保留相容性）"""
        return self._find_attachments_by_prefix(pdf_path)


def test_processor():
    """測試處理器功能"""
    processor = DocumentProcessor()

    # 這裡可以加入測試代碼
    print("✅ DocumentProcessor 初始化成功")


if __name__ == "__main__":
    test_processor()