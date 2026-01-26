#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini 智能分析器 - 增強版
專門為公文智能處理設計，提供完整的分析功能
"""

import json
import re
import time
import sys
from typing import Dict, List, Optional
from datetime import datetime

# 設定編碼以支援中文輸出
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except:
    pass

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ Gemini API 套件未安裝，請執行: pip install google-generativeai")

from config import SETTINGS, GEMINI_PROMPTS


class GeminiSmartAnalyzer:
    """Gemini 智能分析器"""

    def __init__(self, api_key: str = None):
        self.is_available = False
        self.model = None
        self.api_key = api_key if api_key is not None else SETTINGS['gemini']['api_key']

        if GEMINI_AVAILABLE and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(SETTINGS['gemini']['model'])
                self.is_available = True
                print("✅ Gemini API 初始化成功")
            except Exception as e:
                print(f"⚠️ Gemini API 初始化失敗: {e}")

    def analyze_document(self, doc_info: Dict, progress_callback=None) -> Dict:
        """全面分析文件"""
        if not self.is_available:
            return {'error': 'Gemini API 未設定或無法使用'}

        try:
            if progress_callback:
                progress_callback("正在使用 Gemini 分析文件...")

            # 準備分析內容
            content = self._prepare_content_for_analysis(doc_info)

            # 建立提示詞 - 使用 f-string 避免格式化問題（參考原本成功的做法）
            prompt = f"""請完整分析以下公文，提供結構化的分析結果：

{content}

請提供以下分析（使用繁體中文）：

1. 精簡主旨（30字內，去除冗詞）
2. 文件類型（如：通知、邀請、調查、會議等）
3. 重要性等級（高/中/低）
4. 關鍵要點（3-5點，每點20字內）
5. 行動項目（需要做什麼，包含截止日期）
6. 重要日期（活動日、截止日等）
7. 聯絡資訊（承辦人、電話、信箱）
8. 建議檔名（格式：YYYY-MM-DD_簡潔主旨）
9. 建議歸檔路徑（基於內容性質建議子目錄）
10. Google整合建議（行事曆或任務？為什麼？）

請以JSON格式回答：
{{
  "refined_subject": "精簡後的主旨",
  "document_type": "文件類型",
  "priority": "高/中/低",
  "key_points": ["要點1", "要點2", "要點3"],
  "action_items": [
    {{"description": "行動描述", "deadline": "截止日期", "priority": "高/中/低"}}
  ],
  "important_dates": [
    {{"date": "日期", "description": "描述", "type": "deadline/event"}}
  ],
  "contact_info": {{
    "name": "承辦人",
    "phone": "電話",
    "email": "信箱"
  }},
  "suggested_filename": "建議檔名（含日期前綴）",
  "suggested_path": "建議歸檔子目錄",
  "google_suggestion": {{
    "type": "calendar/task",
    "reason": "建議原因",
    "title": "事件標題",
    "description": "詳細描述",
    "due_date": "到期日期"
  }}
}}"""

            # 呼叫 Gemini API
            response = self._call_gemini_api(prompt)

            if 'error' in response:
                return response

            # 解析並驗證回應
            analysis = self._parse_and_validate_response(response['text'], doc_info)

            if progress_callback:
                progress_callback("分析完成！")

            return analysis

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"   ❌ 分析過程詳細錯誤:")
            print(f"      {error_detail}")
            return {'error': f'分析過程發生錯誤: {str(e)}'}

    def _prepare_content_for_analysis(self, doc_info: Dict) -> str:
        """準備分析內容"""
        content_parts = []

        # 基本資訊
        content_parts.append("【文件資訊】")
        content_parts.append(f"檔案名稱：{doc_info.get('file_name', '')}")

        # 檢查是否有錯誤
        if doc_info.get('error'):
            content_parts.append(f"處理錯誤：{doc_info['error']}")

        # 元數據
        metadata = doc_info.get('metadata', {})
        if metadata:
            content_parts.append("\n【公文資訊】")
            for key, value in metadata.items():
                if value and value.strip():
                    # 限制元數據長度
                    if len(str(value)) > 200:
                        value = str(value)[:200] + "..."
                    content_parts.append(f"{key}：{value}")

        # 主要內容段落
        sections = doc_info.get('sections', {})
        exclude_sections = SETTINGS['pdf_processing']['exclude_sections']
        total_content_length = 0
        max_total_length = 8000  # 總內容限制

        for section_name, content in sections.items():
            if section_name not in exclude_sections and content and content.strip():
                content_parts.append(f"\n【{section_name}】")

                # 限制單個段落長度，並考慮總長度
                if len(content) > 1500:
                    content = content[:1500] + "..."

                content_parts.append(content)
                total_content_length += len(content)

                # 如果總內容太長，停止添加更多段落
                if total_content_length > max_total_length:
                    content_parts.append("\n[內容過長，已截斷...]")
                    break

        # 日期資訊
        dates = doc_info.get('dates', [])
        if dates:
            content_parts.append("\n【識別到的日期】")
            for date in dates[:5]:  # 最多顯示5個日期
                if isinstance(date, dict):
                    content_parts.append(f"- {date.get('raw', date)} ({date.get('type', 'date')})")
                else:
                    content_parts.append(f"- {date}")

        # 附件資訊
        attachments = doc_info.get('attachments', [])
        if attachments:
            content_parts.append("\n【附件檔案】")
            for att in attachments[:10]:  # 最多顯示10個附件
                content_parts.append(f"- {att['filename']}")
            if len(attachments) > 10:
                content_parts.append(f"- ... 還有 {len(attachments) - 10} 個附件")

        final_content = '\n'.join(content_parts)

        # 最終長度檢查
        if len(final_content) > 10000:
            final_content = final_content[:10000] + "\n\n[內容已截斷以符合API限制]"

        print(f"   📝 準備分析內容，長度: {len(final_content)} 字元")
        return final_content

    def _call_gemini_api(self, prompt: str, max_retries: int = 3) -> Dict:
        """呼叫 Gemini API，包含重試機制"""
        for attempt in range(max_retries):
            try:
                print(f"   🤖 呼叫 Gemini API (嘗試 {attempt + 1}/{max_retries})...")

                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        temperature=SETTINGS['gemini']['temperature'],
                        max_output_tokens=SETTINGS['gemini']['max_tokens'],
                    )
                )

                if response and hasattr(response, 'text') and response.text:
                    print(f"   ✅ API 回應成功，長度: {len(response.text)} 字元")
                    return {'text': response.text}
                elif response and hasattr(response, 'prompt_feedback'):
                    # 檢查是否因為安全性原因被阻擋
                    feedback = response.prompt_feedback
                    if feedback.block_reason:
                        return {'error': f'內容被阻擋: {feedback.block_reason}'}
                else:
                    print(f"   ⚠️ API 回應為空")
                    return {'error': 'API 回應為空'}

            except Exception as e:
                error_msg = str(e)
                print(f"   ❌ API 呼叫失敗: {error_msg}")

                # 特定錯誤處理
                if "quota" in error_msg.lower():
                    return {'error': f'API 配額不足: {error_msg}'}
                elif "api_key" in error_msg.lower():
                    return {'error': f'API Key 錯誤: {error_msg}'}
                elif "permission" in error_msg.lower():
                    return {'error': f'權限錯誤: {error_msg}'}

                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"   ⏳ {wait_time} 秒後重試...")
                    time.sleep(wait_time)
                else:
                    import traceback
                    print(f"   詳細錯誤: {traceback.format_exc()}")
                    return {'error': f'API 呼叫失敗: {error_msg}'}

        return {'error': '達到最大重試次數'}

    def _parse_and_validate_response(self, response_text: str, doc_info: Dict) -> Dict:
        """解析並驗證 API 回應"""
        try:
            print(f"   🔍 解析 API 回應...")

            # 清理回應文字
            original_text = response_text
            response_text = response_text.strip()

            # 移除 markdown 代碼塊標記
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            # 更積極的清理
            response_text = response_text.strip()

            # 尋找JSON內容
            # 有時候回應會有額外的說明文字，我們需要提取JSON部分
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)

            print(f"   📝 清理後的JSON長度: {len(response_text)} 字元")

            # 解析 JSON
            analysis = json.loads(response_text)
            print(f"   ✅ JSON 解析成功")

            # 驗證和修正分析結果
            analysis = self._validate_and_fix_analysis(analysis, doc_info)

            return analysis

        except json.JSONDecodeError as e:
            print(f"   ❌ JSON 解析失敗: {e}")
            print(f"   原始回應前500字元: {original_text[:500]}...")

            # 將完整回應儲存到檔案供檢查
            try:
                with open('gemini_response_debug.txt', 'w', encoding='utf-8') as f:
                    f.write("=== 原始 Gemini 回應 ===\n")
                    f.write(original_text)
                    f.write("\n\n=== 清理後的回應 ===\n")
                    f.write(response_text)
                print(f"   📁 完整回應已儲存到 gemini_response_debug.txt")
            except Exception as save_error:
                print(f"   ⚠️ 無法儲存調試檔案: {save_error}")

            # 嘗試修復常見的JSON問題
            try:
                fixed_response = self._fix_json_response(response_text)
                if fixed_response:
                    analysis = json.loads(fixed_response)
                    print(f"   ✅ JSON 修復成功")
                    return self._validate_and_fix_analysis(analysis, doc_info)
            except Exception as fix_error:
                print(f"   ⚠️ JSON 修復也失敗: {fix_error}")

            # JSON 解析失敗，使用文字解析
            print(f"   🔄 改用文字解析...")
            return self._parse_text_response(original_text, doc_info)

        except Exception as e:
            print(f"   ❌ 解析過程發生其他錯誤: {e}")
            return self._parse_text_response(original_text, doc_info)

    def _fix_json_response(self, response_text: str) -> Optional[str]:
        """嘗試修復常見的JSON格式問題"""
        try:
            # 移除可能的前後空白和特殊字元
            response_text = response_text.strip()

            # 修復常見的引號問題
            response_text = response_text.replace('"', '"').replace('"', '"')
            response_text = response_text.replace(''', "'").replace(''', "'")

            # 修復可能的換行問題
            response_text = re.sub(r'\n\s*"', '\n  "', response_text)

            # 確保JSON以 { 開始和 } 結束
            if not response_text.startswith('{'):
                start_idx = response_text.find('{')
                if start_idx != -1:
                    response_text = response_text[start_idx:]

            if not response_text.endswith('}'):
                end_idx = response_text.rfind('}')
                if end_idx != -1:
                    response_text = response_text[:end_idx + 1]

            return response_text

        except Exception:
            return None

    def _validate_and_fix_analysis(self, analysis: Dict, doc_info: Dict) -> Dict:
        """驗證和修正分析結果"""
        # 確保必要欄位存在
        required_fields = [
            'refined_subject', 'document_type', 'priority', 'key_points',
            'action_items', 'important_dates', 'contact_info',
            'suggested_filename', 'suggested_path', 'google_suggestion'
        ]

        for field in required_fields:
            if field not in analysis:
                analysis[field] = self._get_default_value(field)

        # 修正檔案名稱（確保有日期前綴）
        if not self._has_date_prefix(analysis['suggested_filename']):
            date_str = self._get_date_string_from_doc(doc_info)
            subject = analysis.get('refined_subject', '未知文件')
            analysis['suggested_filename'] = f"{date_str}_{subject}"

        # 清理檔案名稱中的非法字元
        analysis['suggested_filename'] = self._clean_filename(analysis['suggested_filename'])

        # 確保建議路徑不為空
        if not analysis.get('suggested_path'):
            analysis['suggested_path'] = '一般公文'

        # 驗證 Google 建議
        if not isinstance(analysis.get('google_suggestion'), dict):
            analysis['google_suggestion'] = {
                'type': 'task',
                'reason': '一般公文建議建立任務追蹤',
                'title': analysis.get('refined_subject', '公文處理'),
                'description': '請查看公文內容並採取必要行動',
                'due_date': ''
            }

        return analysis

    def _get_default_value(self, field: str):
        """取得欄位的預設值"""
        defaults = {
            'refined_subject': '未知主旨',
            'document_type': '一般公文',
            'priority': '中',
            'key_points': [],
            'action_items': [],
            'important_dates': [],
            'contact_info': {},
            'suggested_filename': '未命名文件',
            'suggested_path': '一般公文',
            'google_suggestion': {}
        }
        return defaults.get(field, '')

    def _has_date_prefix(self, filename: str) -> bool:
        """檢查檔名是否有日期前綴"""
        return re.match(r'^\d{4}-\d{2}-\d{2}_', filename) is not None

    def _get_date_string_from_doc(self, doc_info: Dict) -> str:
        """從文件中取得日期字串"""
        dates = doc_info.get('dates', [])
        if dates:
            date = dates[0]
            year = date['year'] + 1911
            month = str(date['month']).zfill(2)
            day = str(date['day']).zfill(2)
            return f"{year}-{month}-{day}"
        else:
            return datetime.now().strftime('%Y-%m-%d')

    def _clean_filename(self, filename: str) -> str:
        """清理檔案名稱"""
        # 移除非法字元
        illegal_chars = SETTINGS['file_processing']['illegal_chars']
        replacement_char = SETTINGS['file_processing']['replacement_char']

        cleaned = re.sub(illegal_chars, replacement_char, filename)

        # 限制長度
        max_length = SETTINGS['file_processing']['max_subject_length']
        if len(cleaned) > max_length:
            # 保留日期前綴
            if self._has_date_prefix(cleaned):
                date_part = cleaned[:11]  # YYYY-MM-DD_
                subject_part = cleaned[11:max_length-11]
                cleaned = date_part + subject_part
            else:
                cleaned = cleaned[:max_length]

        return cleaned.strip(' ._-')

    def _parse_text_response(self, response_text: str, doc_info: Dict) -> Dict:
        """解析純文字回應（備用方法）"""
        print("⚠️ JSON 解析失敗，使用文字解析")

        analysis = {
            'refined_subject': '未知主旨',
            'document_type': '一般公文',
            'priority': '中',
            'key_points': [],
            'action_items': [],
            'important_dates': [],
            'contact_info': {},
            'suggested_filename': self._get_date_string_from_doc(doc_info) + '_未命名文件',
            'suggested_path': '一般公文',
            'google_suggestion': {
                'type': 'task',
                'reason': '文字解析備用建議',
                'title': '公文處理',
                'description': '請檢查公文內容並採取行動',
                'due_date': ''
            }
        }

        # 嘗試從文字中提取一些基本資訊
        lines = response_text.split('\n')
        for line in lines:
            line = line.strip()
            if '主旨' in line or '標題' in line:
                # 嘗試提取主旨
                parts = line.split('：')
                if len(parts) > 1:
                    analysis['refined_subject'] = parts[1].strip()[:30]

        return analysis

    def generate_filename(self, subject: str, date: str = None, doc_type: str = None) -> str:
        """生成檔案名稱"""
        if not self.is_available:
            return f"{date or datetime.now().strftime('%Y-%m-%d')}_{subject[:20]}"

        try:
            prompt = GEMINI_PROMPTS['filename_generation'].format(
                subject=subject,
                date=date or '今天',
                type=doc_type or '一般公文'
            )

            response = self._call_gemini_api(prompt)
            if 'error' not in response:
                filename = response['text'].strip()
                return self._clean_filename(filename)

        except Exception as e:
            print(f"⚠️ 檔名生成失敗: {e}")

        # 備用方案
        date_str = date or datetime.now().strftime('%Y-%m-%d')
        return f"{date_str}_{subject[:20]}"

    def suggest_directory(self, content: str) -> str:
        """建議歸檔目錄"""
        if not self.is_available:
            return '一般公文'

        try:
            prompt = GEMINI_PROMPTS['directory_suggestion'].format(content=content[:500])
            response = self._call_gemini_api(prompt)

            if 'error' not in response:
                directory = response['text'].strip()
                return directory if directory else '一般公文'

        except Exception as e:
            print(f"⚠️ 目錄建議失敗: {e}")

        return '一般公文'


def test_analyzer():
    """測試分析器功能"""
    # 檢查 API 可用性
    if not GEMINI_AVAILABLE:
        print("❌ 請安裝 google-generativeai 套件")
        return

    analyzer = GeminiSmartAnalyzer()
    if analyzer.is_available:
        print("✅ GeminiSmartAnalyzer 初始化成功")
    else:
        print("❌ Gemini API 設定有問題")


if __name__ == "__main__":
    test_analyzer()