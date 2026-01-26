#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能檔案管理器
基於 Gemini 分析結果進行檔案組織，移除傳統分類功能
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from config import SETTINGS


class SmartFileManager:
    """智能檔案管理器"""

    def __init__(self):
        self.target_base = Path(SETTINGS['paths']['target_directory'])
        self.settings = SETTINGS['file_processing']

        # 確保目標目錄存在
        self.target_base.mkdir(parents=True, exist_ok=True)

    def organize_document(self, source_file: str, doc_info: Dict, analysis: Dict, google_result: Dict = None) -> Dict:
        """組織文件：重命名、搬移、整理附件"""
        try:
            # 1. 準備目標路徑
            target_info = self._prepare_target_path(analysis, doc_info)

            # 2. 建立目標目錄
            target_dir = self._create_target_directory(target_info)

            # 3. 搬移並重命名主文件
            main_file_result = self._move_main_file(source_file, target_dir, target_info)

            # 4. 搬移附件
            attachment_results = self._move_attachments(
                source_file, target_dir, doc_info.get('attachments', [])
            )

            # 5. 建立處理記錄（包含 Google 整合結果）
            self._create_processing_log(target_dir, doc_info, analysis, google_result)

            result = {
                'success': True,
                'target_path': str(target_dir),
                'main_file': main_file_result,
                'attachments': attachment_results,
                'log_created': True
            }

            print(f"✅ 文件組織完成: {target_dir.name}")
            return result

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'target_path': None
            }

    def _prepare_target_path(self, analysis: Dict, doc_info: Dict) -> Dict:
        """準備目標路徑資訊 - 簡化版，不做分類"""
        # 從分析結果取得檔案名稱
        suggested_filename = analysis.get('suggested_filename', '')
        if not suggested_filename:
            # 備用檔名生成
            date_str = self._extract_date_from_doc(doc_info)
            subject = analysis.get('refined_subject', '未知文件')
            suggested_filename = f"{date_str}_{subject}"

        # 清理檔名，用作資料夾名稱
        clean_filename = self._sanitize_filename(suggested_filename)

        # 直接放在公文智能歸檔根目錄，不做子分類
        return {
            'filename': clean_filename,
            'subdirectory': '',  # 不使用子目錄
            'full_path': self.target_base / clean_filename
        }

    def _create_target_directory(self, target_info: Dict) -> Path:
        """建立目標目錄，如果已存在就先保留"""
        target_dir = target_info['full_path']

        # 建立目錄（如果已存在也沒關係，先保留）
        target_dir.mkdir(parents=True, exist_ok=True)

        if target_dir.exists():
            print(f"📁 使用目錄: {target_dir.name}")
        else:
            print(f"📁 建立目錄: {target_dir.name}")

        return target_dir

    def _move_main_file(self, source_file: str, target_dir: Path, target_info: Dict) -> Dict:
        """搬移並重命名主文件"""
        source_path = Path(source_file)

        # 使用目錄名稱作為檔案名稱（保持一致性）
        new_filename = f"{target_dir.name}{source_path.suffix}"
        target_file = target_dir / new_filename

        try:
            # 如果目標檔案已存在，先刪除（覆蓋）
            if target_file.exists():
                print(f"🗑️ 覆蓋現有檔案: {new_filename}")
                target_file.unlink()

            # 搬移檔案
            shutil.move(str(source_path), str(target_file))

            result = {
                'success': True,
                'original_name': source_path.name,
                'new_name': new_filename,
                'target_path': str(target_file)
            }

            print(f"📄 主文件已搬移: {source_path.name} → {new_filename}")
            return result

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'original_name': source_path.name
            }

    def _move_attachments(self, source_file: str, target_dir: Path, attachments: List[Dict]) -> List[Dict]:
        """搬移附件檔案"""
        results = []

        for attachment in attachments:
            try:
                source_att = Path(attachment['path'])
                if source_att.exists():
                    target_att = target_dir / source_att.name

                    # 如果目標附件已存在，直接覆蓋
                    if target_att.exists():
                        print(f"🗑️ 覆蓋現有附件: {target_att.name}")
                        target_att.unlink()

                    shutil.move(str(source_att), str(target_att))

                    results.append({
                        'success': True,
                        'original_name': source_att.name,
                        'new_name': target_att.name,
                        'target_path': str(target_att)
                    })

                    print(f"📎 附件已搬移: {source_att.name}")

                else:
                    results.append({
                        'success': False,
                        'error': '附件檔案不存在',
                        'original_name': attachment.get('filename', '未知')
                    })

            except Exception as e:
                results.append({
                    'success': False,
                    'error': str(e),
                    'original_name': attachment.get('filename', '未知')
                })

        return results

    def _create_processing_log(self, target_dir: Path, doc_info: Dict, analysis: Dict, google_result: Dict = None) -> None:
        """建立處理記錄檔（總是覆蓋舊記錄）"""
        try:
            log_file = target_dir / "處理記錄.txt"

            # 如果舊記錄存在，先刪除
            if log_file.exists():
                log_file.unlink()
                print(f"🗑️ 覆蓋舊的處理記錄")

            log_content = [
                "公文智能處理系統 - 處理記錄",
                "=" * 50,
                f"處理時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"原始檔案: {doc_info.get('file_name', '')}",
                "",
                "AI 分析結果:",
                f"  主旨: {analysis.get('refined_subject', '')}",
                f"  文件類型: {analysis.get('document_type', '')}",
                f"  重要性: {analysis.get('priority', '')}",
                "",
                "關鍵要點:",
            ]

            # 加入關鍵要點
            key_points = analysis.get('key_points', [])
            if key_points:
                for point in key_points:
                    log_content.append(f"  - {point}")
            else:
                log_content.append("  無")

            # 加入行動項目
            action_items = analysis.get('action_items', [])
            if action_items:
                log_content.append("\n行動項目:")
                for action in action_items:
                    description = action.get('description', '')
                    deadline = action.get('deadline', '')
                    log_content.append(f"  - {description} {f'(截止: {deadline})' if deadline else ''}")
            else:
                log_content.append("\n行動項目: 無")

            # 加入重要日期
            important_dates = analysis.get('important_dates', [])
            if important_dates:
                log_content.append("\n重要日期:")
                for date_info in important_dates:
                    date = date_info.get('date', '')
                    desc = date_info.get('description', '')
                    log_content.append(f"  - {date}: {desc}")
            else:
                log_content.append("\n重要日期: 無")

            # 加入聯絡資訊
            contact = analysis.get('contact_info', {})
            if contact and (contact.get('name') or contact.get('phone') or contact.get('email')):
                log_content.append("\n聯絡資訊:")
                if contact.get('name'):
                    log_content.append(f"  承辦人: {contact['name']}")
                if contact.get('phone'):
                    log_content.append(f"  電話: {contact['phone']}")
                if contact.get('email'):
                    log_content.append(f"  信箱: {contact['email']}")
            else:
                log_content.append("\n聯絡資訊: 無")

            # 加入 Google 整合記錄
            if google_result:
                log_content.append("\nGoogle 整合記錄:")
                log_content.append(f"  類型: {google_result.get('type', '未知')}")
                log_content.append(f"  狀態: {'成功' if google_result.get('success') else '失敗'}")
                if google_result.get('success'):
                    log_content.append(f"  標題: {google_result.get('title', '')}")
                    if google_result.get('date'):
                        log_content.append(f"  日期: {google_result.get('date', '')}")
                    if google_result.get('url'):
                        log_content.append(f"  連結: {google_result.get('url', '')}")
                else:
                    log_content.append(f"  錯誤: {google_result.get('error', '')}")
            else:
                log_content.append("\nGoogle 整合記錄: 未執行")

            log_content.append(f"\n{'=' * 50}")
            log_content.append("※ 此記錄由公文智能處理系統自動生成")

            # 寫入檔案（使用 'w' 模式確保覆蓋）
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(log_content))

            print(f"📝 處理記錄已更新")

        except Exception as e:
            print(f"⚠️ 無法建立處理記錄: {e}")

    def _extract_date_from_doc(self, doc_info: Dict) -> str:
        """從文件資訊中提取日期"""
        dates = doc_info.get('dates', [])
        if dates:
            date = dates[0]
            year = date['year'] + 1911
            month = str(date['month']).zfill(2)
            day = str(date['day']).zfill(2)
            return f"{year}-{month}-{day}"
        else:
            return datetime.now().strftime('%Y-%m-%d')

    def _sanitize_filename(self, filename: str) -> str:
        """清理檔案名稱"""
        # 移除非法字元
        illegal_chars = self.settings['illegal_chars']
        replacement_char = self.settings['replacement_char']

        cleaned = filename
        for char in ['<', '>', ':', '"', '/', '\\', '|', '?', '*']:
            cleaned = cleaned.replace(char, replacement_char)

        # 移除多餘的空白和符號
        cleaned = ' '.join(cleaned.split())
        cleaned = cleaned.strip(' ._-')

        # 限制長度
        max_length = self.settings['max_subject_length']
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length].rstrip(' ._-')

        return cleaned if cleaned else '未命名文件'

    def _sanitize_path(self, path: str) -> str:
        """清理路徑名稱"""
        # 移除路徑中的非法字元
        illegal_chars = ['<', '>', ':', '"', '|', '?', '*']
        cleaned = path

        for char in illegal_chars:
            cleaned = cleaned.replace(char, '_')

        # 標準化路徑分隔符號
        cleaned = cleaned.replace('/', os.sep).replace('\\', os.sep)

        return cleaned.strip(' ._-') if cleaned else '一般公文'

    def get_target_directory_info(self, analysis: Dict) -> Dict:
        """取得目標目錄資訊（不實際建立）"""
        suggested_path = analysis.get('suggested_path', '一般公文')
        clean_path = self._sanitize_path(suggested_path)
        full_path = self.target_base / clean_path

        return {
            'base_directory': str(self.target_base),
            'subdirectory': clean_path,
            'full_path': str(full_path),
            'exists': full_path.exists()
        }

    def cleanup_empty_directories(self) -> List[str]:
        """清理空目錄"""
        removed_dirs = []

        try:
            for root, dirs, files in os.walk(self.target_base, topdown=False):
                for dir_name in dirs:
                    dir_path = Path(root) / dir_name
                    if dir_path.is_dir() and not any(dir_path.iterdir()):
                        dir_path.rmdir()
                        removed_dirs.append(str(dir_path))

        except Exception as e:
            print(f"⚠️ 清理空目錄時發生錯誤: {e}")

        return removed_dirs


def test_file_manager():
    """測試檔案管理器功能"""
    manager = SmartFileManager()
    print(f"✅ SmartFileManager 初始化成功")
    print(f"   目標目錄: {manager.target_base}")


if __name__ == "__main__":
    test_file_manager()