#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google 整合模組 - 簡化版
基於 Gemini 分析結果建立 Google Calendar 事件或 Tasks
"""

import os
import pickle
import re
from datetime import datetime, timedelta
from typing import Dict, Optional, List

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False
    print("⚠️ Google API 套件未安裝，請執行: pip install google-api-python-client google-auth google-auth-oauthlib")

from config import SETTINGS


class GoogleIntegration:
    """Google Calendar & Tasks 整合"""

    def __init__(self, auto_auth=True):
        self.scopes = SETTINGS['google']['scopes']
        self.timezone = SETTINGS['google']['timezone']
        self.creds = None
        self.calendar_service = None
        self.tasks_service = None
        self.is_authenticated = False

        if GOOGLE_API_AVAILABLE and auto_auth:
            self._authenticate()

    def _authenticate(self):
        """Google 認證 - 改善版本，自動處理憑證刷新"""
        token_path = SETTINGS['paths']['token']
        credentials_path = SETTINGS['paths']['credentials']

        try:
            # 載入已存在的憑證
            if os.path.exists(token_path):
                try:
                    with open(token_path, 'rb') as token:
                        self.creds = pickle.load(token)
                    print("已載入儲存的憑證")
                except Exception as e:
                    print(f"載入憑證檔案失敗: {e}")
                    # 刪除損壞的憑證檔案
                    if os.path.exists(token_path):
                        os.remove(token_path)
                    self.creds = None

            # 檢查並處理憑證狀態
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    print("憑證已過期，嘗試自動刷新...")
                    try:
                        self.creds.refresh(Request())
                        print("憑證刷新成功")

                        # 儲存刷新後的憑證
                        with open(token_path, 'wb') as token:
                            pickle.dump(self.creds, token)
                        print("已儲存更新的憑證")

                    except Exception as refresh_error:
                        print(f"憑證刷新失敗: {refresh_error}")
                        print("嘗試重新授權...")

                        # 刪除無效的token檔案
                        if os.path.exists(token_path):
                            os.remove(token_path)
                        self.creds = None

                        # 進行完整重新授權
                        self._perform_full_auth(credentials_path, token_path)
                else:
                    print("執行初次授權...")
                    self._perform_full_auth(credentials_path, token_path)

            # 建立服務並測試連線
            if self.creds and self.creds.valid:
                try:
                    self.calendar_service = build('calendar', 'v3', credentials=self.creds)
                    self.tasks_service = build('tasks', 'v1', credentials=self.creds)

                    # 簡單測試API是否可用
                    self.calendar_service.calendarList().list(maxResults=1).execute()

                    self.is_authenticated = True
                    print("Google API 認證成功並已測試連線")

                except Exception as api_error:
                    print(f"API 連線測試失敗: {api_error}")
                    print("嘗試重新授權...")

                    # API呼叫失敗，可能是憑證問題，重新授權
                    if os.path.exists(token_path):
                        os.remove(token_path)
                    self._perform_full_auth(credentials_path, token_path)

                    # 再次嘗試建立服務
                    if self.creds and self.creds.valid:
                        self.calendar_service = build('calendar', 'v3', credentials=self.creds)
                        self.tasks_service = build('tasks', 'v1', credentials=self.creds)
                        self.is_authenticated = True
                        print("重新授權後連線成功")
            else:
                self.is_authenticated = False
                print("無法取得有效憑證")

        except Exception as e:
            print(f"Google 認證過程發生錯誤: {e}")
            self.is_authenticated = False

    def _perform_full_auth(self, credentials_path, token_path):
        """執行完整的OAuth授權流程"""
        try:
            if not os.path.exists(credentials_path):
                print(f"找不到 Google 認證檔案: {credentials_path}")
                return

            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, self.scopes)

            # 使用本地伺服器進行授權
            self.creds = flow.run_local_server(port=0)

            # 儲存新的憑證
            with open(token_path, 'wb') as token:
                pickle.dump(self.creds, token)
            print("已儲存新的授權憑證")

        except Exception as e:
            print(f"完整授權流程失敗: {e}")
            self.creds = None

    def _ensure_valid_credentials(self):
        """確保憑證有效，必要時自動刷新"""
        if not self.creds or not self.creds.valid:
            print("偵測到憑證問題，嘗試重新認證...")
            self._authenticate()
            return self.is_authenticated

        # 檢查憑證是否即將過期（提前5分鐘刷新）
        if self.creds.expired or (hasattr(self.creds, 'expiry') and
                                  self.creds.expiry and
                                  (self.creds.expiry - datetime.utcnow()).total_seconds() < 300):
            print("憑證即將過期，提前刷新...")
            try:
                if self.creds.refresh_token:
                    self.creds.refresh(Request())
                    # 儲存刷新後的憑證
                    token_path = SETTINGS['paths']['token']
                    with open(token_path, 'wb') as token:
                        pickle.dump(self.creds, token)
                    print("憑證提前刷新成功")
                else:
                    print("無refresh_token，執行完整重新認證...")
                    self._authenticate()
            except Exception as e:
                print(f"憑證刷新失敗: {e}")
                self._authenticate()

        return self.is_authenticated

    def create_from_analysis(self, analysis: Dict) -> Dict:
        """根據分析結果建立 Google 事件或任務"""
        # 確保憑證有效
        if not self._ensure_valid_credentials():
            return {'success': False, 'error': 'Google API 認證失敗'}

        try:
            google_suggestion = analysis.get('google_suggestion', {})
            suggestion_type = google_suggestion.get('type', 'task')

            if suggestion_type.lower() == 'calendar':
                return self._create_calendar_event(analysis, google_suggestion)
            else:
                return self._create_task(analysis, google_suggestion)

        except Exception as e:
            # 如果失敗，可能是憑證問題，嘗試重新認證後再試一次
            if "credentials" in str(e).lower() or "unauthorized" in str(e).lower():
                print("偵測到認證錯誤，嘗試重新認證...")
                self._authenticate()
                if self.is_authenticated:
                    try:
                        if suggestion_type.lower() == 'calendar':
                            return self._create_calendar_event(analysis, google_suggestion)
                        else:
                            return self._create_task(analysis, google_suggestion)
                    except Exception as retry_error:
                        return {'success': False, 'error': f'重試後仍失敗: {str(retry_error)}'}

            return {'success': False, 'error': f'建立 Google 項目失敗: {str(e)}'}

    def _create_calendar_event(self, analysis: Dict, suggestion: Dict) -> Dict:
        """建立行事曆事件"""
        try:
            title = suggestion.get('title', analysis.get('refined_subject', '公文事件'))
            description = self._build_event_description(analysis, suggestion)

            # 檢查是否有用戶指定的自定義日期
            if 'custom_date' in suggestion:
                event_date = suggestion['custom_date']
                print(f"   📅 使用指定日期: {event_date.strftime('%Y-%m-%d %H:%M')}")
            else:
                # 解析建議的日期
                due_date = suggestion.get('due_date', '')
                event_date = self._parse_date(due_date)

                if not event_date:
                    print(f"   ⚠️ 無法從公文中識別日期")
                    return {'success': False, 'error': '無法識別公文中的相關日期，請在建立時手動指定日期'}

            # 建立事件
            event = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': event_date.isoformat(),
                    'timeZone': self.timezone,
                },
                'end': {
                    'dateTime': (event_date + timedelta(hours=1)).isoformat(),
                    'timeZone': self.timezone,
                },
                'reminders': {
                    'useDefault': SETTINGS['google']['default_reminder'],
                },
            }

            # 建立事件
            result = self.calendar_service.events().insert(
                calendarId='primary',
                body=event
            ).execute()

            return {
                'success': True,
                'type': 'calendar',
                'id': result['id'],
                'title': title,
                'date': event_date.strftime('%Y-%m-%d %H:%M'),
                'url': result.get('htmlLink', '')
            }

        except Exception as e:
            return {'success': False, 'error': f'建立行事曆事件失敗: {str(e)}'}

    def _create_task(self, analysis: Dict, suggestion: Dict) -> Dict:
        """建立任務"""
        try:
            title = suggestion.get('title', analysis.get('refined_subject', '公文處理'))
            notes = self._build_task_notes(analysis, suggestion)

            # 檢查是否有用戶指定的自定義日期
            if 'custom_date' in suggestion:
                task_due = suggestion['custom_date']
                print(f"   📅 使用指定截止日期: {task_due.strftime('%Y-%m-%d')}")
            else:
                # 解析建議的到期日
                due_date = suggestion.get('due_date', '')
                task_due = self._parse_date(due_date)

            # 建立任務
            task = {
                'title': title,
                'notes': notes,
            }

            if task_due:
                task['due'] = task_due.strftime('%Y-%m-%dT%H:%M:%S.000Z')

            # 建立任務
            result = self.tasks_service.tasks().insert(
                tasklist='@default',
                body=task
            ).execute()

            return {
                'success': True,
                'type': 'task',
                'id': result['id'],
                'title': title,
                'due_date': task_due.strftime('%Y-%m-%d') if task_due else '',
                'url': f"https://tasks.google.com/embed/list/{result['id']}"
            }

        except Exception as e:
            return {'success': False, 'error': f'建立任務失敗: {str(e)}'}

    def _build_event_description(self, analysis: Dict, suggestion: Dict) -> str:
        """建立行事曆事件描述"""
        parts = []

        # 基本資訊
        doc_type = analysis.get('document_type', '')
        priority = analysis.get('priority', '')
        if doc_type:
            parts.append(f"文件類型：{doc_type}")
        if priority:
            parts.append(f"重要性：{priority}")

        # 關鍵要點
        key_points = analysis.get('key_points', [])
        if key_points:
            parts.append("\n關鍵要點：")
            for point in key_points[:3]:  # 最多顯示3個要點
                parts.append(f"• {point}")

        # 行動項目
        action_items = analysis.get('action_items', [])
        if action_items:
            parts.append("\n需要行動：")
            for action in action_items[:3]:  # 最多顯示3個行動
                desc = action.get('description', '')
                deadline = action.get('deadline', '')
                if desc:
                    parts.append(f"• {desc} {f'(截止: {deadline})' if deadline else ''}")

        # 聯絡資訊
        contact = analysis.get('contact_info', {})
        if contact:
            parts.append("\n聯絡資訊：")
            if contact.get('name'):
                parts.append(f"承辦人：{contact['name']}")
            if contact.get('phone'):
                parts.append(f"電話：{contact['phone']}")
            if contact.get('email'):
                parts.append(f"信箱：{contact['email']}")

        # AI 建議原因
        reason = suggestion.get('reason', '')
        if reason:
            parts.append(f"\n建議原因：{reason}")

        parts.append("\n[由公文智能處理系統自動建立]")

        return '\n'.join(parts)

    def _build_task_notes(self, analysis: Dict, suggestion: Dict) -> str:
        """建立任務備註"""
        parts = []

        # 基本資訊
        doc_type = analysis.get('document_type', '')
        priority = analysis.get('priority', '')
        if doc_type:
            parts.append(f"文件類型：{doc_type}")
        if priority:
            parts.append(f"重要性：{priority}")

        # 行動項目
        action_items = analysis.get('action_items', [])
        if action_items:
            parts.append("\n待辦事項：")
            for i, action in enumerate(action_items, 1):
                desc = action.get('description', '')
                deadline = action.get('deadline', '')
                priority_level = action.get('priority', '')

                if desc:
                    line = f"{i}. {desc}"
                    if deadline:
                        line += f" (截止: {deadline})"
                    if priority_level:
                        line += f" [{priority_level}]"
                    parts.append(line)

        # 重要日期
        important_dates = analysis.get('important_dates', [])
        if important_dates:
            parts.append("\n重要日期：")
            for date_info in important_dates:
                date = date_info.get('date', '')
                desc = date_info.get('description', '')
                if date and desc:
                    parts.append(f"• {date}: {desc}")

        # 聯絡資訊
        contact = analysis.get('contact_info', {})
        if contact:
            parts.append("\n聯絡資訊：")
            if contact.get('name'):
                parts.append(f"承辦人：{contact['name']}")
            if contact.get('phone'):
                parts.append(f"電話：{contact['phone']}")
            if contact.get('email'):
                parts.append(f"信箱：{contact['email']}")

        parts.append("\n[由公文智能處理系統自動建立]")

        return '\n'.join(parts)

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """解析日期字串"""
        if not date_str:
            return None

        try:
            # 民國年格式: 114年9月15日
            roc_match = re.search(r'(\d{2,3})年(\d{1,2})月(\d{1,2})日', date_str)
            if roc_match:
                year = int(roc_match.group(1)) + 1911
                month = int(roc_match.group(2))
                day = int(roc_match.group(3))
                return datetime(year, month, day, 9, 0)  # 預設上午9點

            # 西元年格式: 2024-12-15
            western_match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', date_str)
            if western_match:
                year = int(western_match.group(1))
                month = int(western_match.group(2))
                day = int(western_match.group(3))
                return datetime(year, month, day, 9, 0)

            # 其他格式可以在這裡添加

        except (ValueError, AttributeError):
            pass

        return None

    def list_calendars(self) -> List[Dict]:
        """列出可用的行事曆"""
        if not self.is_authenticated:
            return []

        try:
            calendars_result = self.calendar_service.calendarList().list().execute()
            calendars = calendars_result.get('items', [])

            return [
                {
                    'id': cal['id'],
                    'name': cal['summary'],
                    'primary': cal.get('primary', False)
                }
                for cal in calendars
            ]

        except Exception as e:
            print(f"⚠️ 無法取得行事曆列表: {e}")
            return []

    def list_task_lists(self) -> List[Dict]:
        """列出可用的任務清單"""
        if not self.is_authenticated:
            return []

        try:
            tasklists_result = self.tasks_service.tasklists().list().execute()
            tasklists = tasklists_result.get('items', [])

            return [
                {
                    'id': tl['id'],
                    'name': tl['title']
                }
                for tl in tasklists
            ]

        except Exception as e:
            print(f"⚠️ 無法取得任務清單: {e}")
            return []

    def test_connection(self) -> Dict:
        """測試 Google API 連線"""
        if not GOOGLE_API_AVAILABLE:
            return {
                'success': False,
                'error': 'Google API 套件未安裝'
            }

        if not self.is_authenticated:
            return {
                'success': False,
                'error': 'Google API 未認證'
            }

        try:
            # 測試 Calendar API
            calendars = self.list_calendars()
            # 測試 Tasks API
            task_lists = self.list_task_lists()

            return {
                'success': True,
                'calendar_count': len(calendars),
                'tasklist_count': len(task_lists),
                'authenticated': True
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'連線測試失敗: {str(e)}'
            }


def test_google_integration():
    """測試 Google 整合功能"""
    if not GOOGLE_API_AVAILABLE:
        print("❌ 請安裝 Google API 套件")
        return

    integration = GoogleIntegration()
    result = integration.test_connection()

    if result['success']:
        print("✅ Google 整合測試成功")
        print(f"   行事曆數量: {result['calendar_count']}")
        print(f"   任務清單數量: {result['tasklist_count']}")
    else:
        print(f"❌ Google 整合測試失敗: {result['error']}")


if __name__ == "__main__":
    test_google_integration()