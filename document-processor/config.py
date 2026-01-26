#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公文智能處理系統設定檔
簡化版本 - 專注於 Gemini API 整合
"""

import os
from pathlib import Path

# 載入 .env 環境變數
try:
    from dotenv import load_dotenv
    # 載入專案目錄下的 .env 檔案
    env_path = Path(__file__).parent / '.env'
    load_dotenv(env_path)
    print(f"✅ 已載入環境變數檔案: {env_path}")
except ImportError:
    print("⚠️ python-dotenv 未安裝，將使用系統環境變數或預設值")
    print("   請執行: pip install python-dotenv")

# 從環境變數取得 API Key
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

if not GEMINI_API_KEY:
    print("⚠️ 未設定 GEMINI_API_KEY！請在 .env 檔案中設定你的 API Key")
    print("   格式: GEMINI_API_KEY=你的API_KEY")

# ===== 主要設定 =====
SETTINGS = {
    # 路徑設定
    'paths': {
        'scan_directory': r"G:\我的雲端硬碟\00.Inbox",  # 掃描路徑
        'target_directory': r"G:\我的雲端硬碟\01.公文智能歸檔",  # 歸檔路徑
        'credentials': 'credentials.json',  # Google 認證檔
        'token': 'token.pickle'  # Google token
    },

    # Gemini API 設定
    'gemini': {
        'api_key': GEMINI_API_KEY,  # 從 .env 檔案讀取
        'model': 'gemini-2.0-flash',  # 2025年推薦使用的免費模型
        'temperature': 0.2,
        'max_tokens': 8192,  # 增加 token 限制以確保完整回應
        'timeout': 30  # 請求超時時間（秒）
    },

    # Google 整合設定
    'google': {
        'scopes': [
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/tasks'
        ],
        'timezone': 'Asia/Taipei',
        'auto_create_events': False,  # 是否自動建立Google事件
        'default_reminder': True
    },

    # 檔案處理設定
    'file_processing': {
        'date_format': '%Y-%m-%d',  # 日期格式
        'max_subject_length': 80,    # 主旨最大長度
        'illegal_chars': r'[<>:"/\\|?*]',  # 非法字元
        'replacement_char': '_',     # 替換字元
        'create_subdirectories': True,  # 是否建立子目錄
        'preserve_original_name': False  # 是否保留原始檔名
    },

    # PDF 處理設定
    'pdf_processing': {
        'noise_patterns': [
            (r'[\.·‧。]{2,}', ''),
            (r'^\s*[\.·‧。]\s*$', ''),
            (r'裝\s*[\.·‧。]*\s*訂\s*[\.·‧。]*\s*線', ''),
            (r'^\s*裝\s*$', ''),
            (r'^\s*訂\s*$', ''),
            (r'^\s*線\s*$', ''),
            (r'第\s*\d+\s*頁[，,]\s*共\s*\d+\s*頁', ''),
            (r'■+[^■\n]*■+', ''),
            (r'收\s*文\s*[:：]\s*\d+/\d+/\d+', ''),
            (r'檔\s*號\s*[:：]', ''),
            (r'保\s*存\s*年\s*限\s*[:：]', ''),
            (r'^\s*\d{1,2}\s*$', ''),
        ],
        'section_patterns': {
            '主旨': r'主\s*旨\s*[:：]\s*',
            '說明': r'說\s*明\s*[:：]\s*',
            '附件': r'附\s*件\s*[:：]\s*',
            '正本': r'正\s*本\s*[:：]\s*',
            '副本': r'副\s*本\s*[:：]\s*',
            '發文日期': r'發\s*文\s*日\s*期\s*[:：]\s*',
            '發文字號': r'發\s*文\s*字\s*號\s*[:：]\s*',
            '速別': r'速\s*別\s*[:：]\s*',
            '受文者': r'受\s*文\s*者\s*[:：]\s*'
        },
        'exclude_sections': ['受文者', '正本', '副本']  # 不分析的段落
    },

    # 系統設定
    'system': {
        'debug_mode': False,
        'log_level': 'INFO',
        'enable_backup': True,
        'backup_directory': 'backup'
    }
}

# ===== Gemini 提示詞模板 =====
GEMINI_PROMPTS = {
    'document_analysis': """請完整分析以下公文內容，提供結構化的分析結果：

{content}

請以JSON格式提供以下分析（使用繁體中文）：

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

請以以下JSON格式回答：
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
}}""",

    'filename_generation': """基於以下公文資訊，請建議一個合適的檔案名稱：

主旨：{subject}
發文日期：{date}
文件類型：{type}

請提供格式為 YYYY-MM-DD_簡潔描述 的檔名，例如：
2024-12-15_教師研習通知
2024-12-20_特教評鑑資料繳交

檔名：""",

    'directory_suggestion': """基於以下公文內容，請建議最適合的歸檔子目錄：

{content}

可選的目錄類型：
- 會議通知
- 研習活動
- 特教業務
- 資訊業務
- 填報調查
- 法規辦法
- 進修部業務
- 其他

請直接回答目錄名稱："""
}

# ===== 驗證設定 =====
def validate_settings():
    """驗證設定是否正確"""
    errors = []

    # 檢查必要路徑
    scan_path = Path(SETTINGS['paths']['scan_directory'])
    if not scan_path.exists():
        errors.append(f"掃描目錄不存在: {scan_path}")

    # 檢查Gemini API Key
    if not SETTINGS['gemini']['api_key'] or SETTINGS['gemini']['api_key'].startswith('your-'):
        errors.append("請設定正確的 Gemini API Key")

    # 檢查Google認證檔
    if not os.path.exists(SETTINGS['paths']['credentials']):
        errors.append("找不到 Google 認證檔案 credentials.json")

    return errors

if __name__ == "__main__":
    errors = validate_settings()
    if errors:
        print("⚠️ 設定檢查發現問題：")
        for error in errors:
            print(f"   - {error}")
    else:
        print("✅ 設定檢查通過！")