#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notion 整合模組
將公文分析結果同步到 Notion 資料庫
"""

import os
import json
from datetime import datetime
from typing import Dict, Optional, List
from pathlib import Path

try:
    from notion_client import Client
    from notion_client.errors import APIResponseError
    NOTION_API_AVAILABLE = True
except ImportError:
    NOTION_API_AVAILABLE = False
    print("Notion API 套件未安裝，請執行: pip install notion-client")


class NotionIntegration:
    """Notion 資料庫整合"""

    # 資料庫結構定義
    TASK_DB_PROPERTIES = {
        "標題": {"title": {}},
        "日期": {"date": {}},
        "類型": {
            "select": {
                "options": [
                    {"name": "活動", "color": "blue"},
                    {"name": "任務", "color": "green"}
                ]
            }
        },
        "優先級": {
            "select": {
                "options": [
                    {"name": "高", "color": "red"},
                    {"name": "中", "color": "yellow"},
                    {"name": "低", "color": "gray"}
                ]
            }
        },
        "狀態": {
            "select": {
                "options": [
                    {"name": "待處理", "color": "default"},
                    {"name": "進行中", "color": "blue"},
                    {"name": "已完成", "color": "green"}
                ]
            }
        }
    }

    ARCHIVE_DB_PROPERTIES = {
        "標題": {"title": {}},
        "歸檔日期": {"date": {}},
        "文件類型": {
            "select": {
                "options": [
                    {"name": "通知", "color": "blue"},
                    {"name": "會議", "color": "purple"},
                    {"name": "研習", "color": "green"},
                    {"name": "調查", "color": "yellow"},
                    {"name": "報告", "color": "orange"},
                    {"name": "其他", "color": "gray"}
                ]
            }
        },
        "優先級": {
            "select": {
                "options": [
                    {"name": "高", "color": "red"},
                    {"name": "中", "color": "yellow"},
                    {"name": "低", "color": "gray"}
                ]
            }
        },
        "歸檔路徑": {"rich_text": {}}
    }

    def __init__(self, api_token: str = None):
        """初始化 Notion 整合"""
        self.api_token = api_token
        self.client = None
        self.is_connected = False
        self.task_db_id = None
        self.archive_db_id = None

        if NOTION_API_AVAILABLE and api_token:
            self._connect()

    def _connect(self):
        """建立 Notion API 連線"""
        try:
            self.client = Client(auth=self.api_token)
            # 測試連線
            self.client.users.me()
            self.is_connected = True
            print("Notion API 連線成功")
        except Exception as e:
            self.is_connected = False
            print(f"Notion API 連線失敗: {e}")

    def set_token(self, api_token: str) -> bool:
        """設定 API Token 並重新連線"""
        self.api_token = api_token
        if NOTION_API_AVAILABLE and api_token:
            self._connect()
        return self.is_connected

    def test_connection(self) -> Dict:
        """測試 Notion API 連線"""
        if not NOTION_API_AVAILABLE:
            return {
                'success': False,
                'error': 'Notion API 套件未安裝，請執行: pip install notion-client'
            }

        if not self.api_token:
            return {
                'success': False,
                'error': '未設定 Notion API Token'
            }

        try:
            user = self.client.users.me()
            return {
                'success': True,
                'user': user.get('name', 'Unknown'),
                'connected': True
            }
        except APIResponseError as e:
            return {
                'success': False,
                'error': f'API 錯誤: {e.message}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'連線失敗: {str(e)}'
            }

    def create_databases(self, parent_page_id: str) -> Dict:
        """在指定頁面下建立任務資料庫和歸檔資料庫"""
        if not self.is_connected:
            return {'success': False, 'error': 'Notion 未連線'}

        results = {
            'success': True,
            'task_db': None,
            'archive_db': None,
            'errors': []
        }

        # 建立任務資料庫
        try:
            task_db = self.client.databases.create(
                parent={"type": "page_id", "page_id": parent_page_id},
                title=[{"type": "text", "text": {"content": "公文任務追蹤"}}],
                properties=self.TASK_DB_PROPERTIES,
                icon={"type": "emoji", "emoji": "📋"}
            )
            self.task_db_id = task_db['id']
            results['task_db'] = {
                'id': task_db['id'],
                'url': task_db['url']
            }
            print(f"已建立任務資料庫: {task_db['id']}")
        except APIResponseError as e:
            results['errors'].append(f'建立任務資料庫失敗: {e.message}')
            results['success'] = False
        except Exception as e:
            results['errors'].append(f'建立任務資料庫失敗: {str(e)}')
            results['success'] = False

        # 建立歸檔資料庫
        try:
            archive_db = self.client.databases.create(
                parent={"type": "page_id", "page_id": parent_page_id},
                title=[{"type": "text", "text": {"content": "公文歸檔記錄"}}],
                properties=self.ARCHIVE_DB_PROPERTIES,
                icon={"type": "emoji", "emoji": "📁"}
            )
            self.archive_db_id = archive_db['id']
            results['archive_db'] = {
                'id': archive_db['id'],
                'url': archive_db['url']
            }
            print(f"已建立歸檔資料庫: {archive_db['id']}")
        except APIResponseError as e:
            results['errors'].append(f'建立歸檔資料庫失敗: {e.message}')
            results['success'] = False
        except Exception as e:
            results['errors'].append(f'建立歸檔資料庫失敗: {str(e)}')
            results['success'] = False

        return results

    def set_database_ids(self, task_db_id: str = None, archive_db_id: str = None):
        """設定已存在的資料庫 ID"""
        if task_db_id:
            self.task_db_id = task_db_id
        if archive_db_id:
            self.archive_db_id = archive_db_id

    def add_task_entry(self, analysis: Dict, event_type: str, event_date: str) -> Dict:
        """
        新增任務/活動到任務資料庫

        Args:
            analysis: Gemini 分析結果
            event_type: 'calendar' 或 'task'
            event_date: 日期字串 (YYYY-MM-DD 或 YYYY-MM-DD HH:MM)
        """
        if not self.is_connected:
            return {'success': False, 'error': 'Notion 未連線'}

        if not self.task_db_id:
            return {'success': False, 'error': '任務資料庫未設定'}

        try:
            # 準備標題
            title = analysis.get('refined_subject', '未命名任務')

            # 準備日期（處理不同格式）
            date_value = self._parse_date_for_notion(event_date)

            # 準備類型
            type_value = "活動" if event_type == 'calendar' else "任務"

            # 準備優先級
            priority = analysis.get('priority', '中')
            if priority not in ['高', '中', '低']:
                priority = '中'

            # 準備摘要內容
            summary_content = self._build_summary_content(analysis)

            # 建立頁面（使用 "Name" 作為標題欄位，這是 Notion 預設的 title 屬性名稱）
            new_page = self.client.pages.create(
                parent={"database_id": self.task_db_id},
                properties={
                    "Name": {
                        "title": [{"text": {"content": title}}]
                    },
                    "日期": {
                        "date": {"start": date_value}
                    },
                    "類型": {
                        "select": {"name": type_value}
                    },
                    "優先級": {
                        "select": {"name": priority}
                    },
                    "狀態": {
                        "select": {"name": "待處理"}
                    }
                },
                children=summary_content
            )

            return {
                'success': True,
                'page_id': new_page['id'],
                'url': new_page['url']
            }

        except APIResponseError as e:
            return {'success': False, 'error': f'API 錯誤: {e.message}'}
        except Exception as e:
            return {'success': False, 'error': f'新增任務失敗: {str(e)}'}

    def add_archive_entry(self, analysis: Dict, folder_name: str, archive_path: str) -> Dict:
        """
        新增歸檔記錄到歸檔資料庫

        Args:
            analysis: Gemini 分析結果
            folder_name: 歸檔資料夾名稱（作為標題）
            archive_path: 完整歸檔路徑
        """
        if not self.is_connected:
            return {'success': False, 'error': 'Notion 未連線'}

        if not self.archive_db_id:
            return {'success': False, 'error': '歸檔資料庫未設定'}

        try:
            # 準備文件類型
            doc_type = analysis.get('document_type', '其他')
            # 映射到資料庫選項
            type_mapping = {
                '通知': '通知',
                '會議': '會議',
                '研習': '研習',
                '調查': '調查',
                '報告': '報告'
            }
            doc_type_value = type_mapping.get(doc_type, '其他')

            # 準備優先級
            priority = analysis.get('priority', '中')
            if priority not in ['高', '中', '低']:
                priority = '中'

            # 準備摘要內容
            summary_content = self._build_summary_content(analysis)

            # 今天日期
            today = datetime.now().strftime('%Y-%m-%d')

            # 建立頁面（使用 "Name" 作為標題欄位）
            new_page = self.client.pages.create(
                parent={"database_id": self.archive_db_id},
                properties={
                    "Name": {
                        "title": [{"text": {"content": folder_name}}]
                    },
                    "歸檔日期": {
                        "date": {"start": today}
                    },
                    "文件類型": {
                        "select": {"name": doc_type_value}
                    },
                    "優先級": {
                        "select": {"name": priority}
                    },
                    "歸檔路徑": {
                        "rich_text": [{"text": {"content": archive_path}}]
                    }
                },
                children=summary_content
            )

            return {
                'success': True,
                'page_id': new_page['id'],
                'url': new_page['url']
            }

        except APIResponseError as e:
            return {'success': False, 'error': f'API 錯誤: {e.message}'}
        except Exception as e:
            return {'success': False, 'error': f'新增歸檔記錄失敗: {str(e)}'}

    def _parse_date_for_notion(self, date_str: str) -> str:
        """解析日期字串為 Notion 格式"""
        if not date_str:
            return datetime.now().strftime('%Y-%m-%d')

        # 如果包含時間
        if ' ' in date_str and ':' in date_str:
            try:
                dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
                return dt.strftime('%Y-%m-%dT%H:%M:%S')
            except ValueError:
                pass

        # 只有日期
        try:
            dt = datetime.strptime(date_str[:10], '%Y-%m-%d')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return datetime.now().strftime('%Y-%m-%d')

    def _build_summary_content(self, analysis: Dict) -> List[Dict]:
        """建立摘要內容區塊"""
        blocks = []

        # 文件類型和優先級
        doc_type = analysis.get('document_type', '')
        priority = analysis.get('priority', '')
        if doc_type or priority:
            blocks.append({
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [{"type": "text", "text": {"content": f"文件類型：{doc_type}　｜　優先級：{priority}"}}],
                    "icon": {"type": "emoji", "emoji": "📄"}
                }
            })

        # 關鍵要點
        key_points = analysis.get('key_points', [])
        if key_points:
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": "關鍵要點"}}]
                }
            })
            for point in key_points:
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": point}}]
                    }
                })

        # 行動項目
        action_items = analysis.get('action_items', [])
        if action_items:
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": "行動項目"}}]
                }
            })
            for item in action_items:
                desc = item.get('description', '')
                deadline = item.get('deadline', '')
                content = desc
                if deadline:
                    content += f"（截止：{deadline}）"
                blocks.append({
                    "object": "block",
                    "type": "to_do",
                    "to_do": {
                        "rich_text": [{"type": "text", "text": {"content": content}}],
                        "checked": False
                    }
                })

        # 重要日期
        important_dates = analysis.get('important_dates', [])
        if important_dates:
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": "重要日期"}}]
                }
            })
            for date_info in important_dates:
                date = date_info.get('date', '')
                desc = date_info.get('description', '')
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": f"{date}：{desc}"}}]
                    }
                })

        # 聯絡資訊
        contact = analysis.get('contact_info', {})
        if contact and any(contact.values()):
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": "聯絡資訊"}}]
                }
            })
            contact_text = []
            if contact.get('name'):
                contact_text.append(f"承辦人：{contact['name']}")
            if contact.get('phone'):
                contact_text.append(f"電話：{contact['phone']}")
            if contact.get('email'):
                contact_text.append(f"信箱：{contact['email']}")

            if contact_text:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": "\n".join(contact_text)}}]
                    }
                })

        # 分隔線
        blocks.append({
            "object": "block",
            "type": "divider",
            "divider": {}
        })

        # 系統標記
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{
                    "type": "text",
                    "text": {"content": "由公文智能處理系統自動建立"},
                    "annotations": {"italic": True, "color": "gray"}
                }]
            }
        })

        return blocks

    def get_status(self) -> Dict:
        """取得 Notion 整合狀態"""
        return {
            'available': NOTION_API_AVAILABLE,
            'connected': self.is_connected,
            'has_token': bool(self.api_token),
            'task_db_id': self.task_db_id,
            'archive_db_id': self.archive_db_id,
            'task_db_ready': bool(self.task_db_id),
            'archive_db_ready': bool(self.archive_db_id)
        }


def test_notion_integration():
    """測試 Notion 整合功能"""
    if not NOTION_API_AVAILABLE:
        print("請安裝 Notion API 套件: pip install notion-client")
        return

    # 從環境變數取得測試用的 Token
    test_token = os.getenv('NOTION_API_TOKEN', '')
    if not test_token:
        print("請設定 NOTION_API_TOKEN 環境變數進行測試")
        return

    integration = NotionIntegration(test_token)
    result = integration.test_connection()

    if result['success']:
        print("Notion 整合測試成功")
        print(f"   使用者: {result.get('user', 'Unknown')}")
    else:
        print(f"Notion 整合測試失敗: {result['error']}")


if __name__ == "__main__":
    test_notion_integration()
