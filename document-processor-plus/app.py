#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公文智能處理系統 Web UI
"""

import os
import sys
import json
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_from_directory

# 加入模組路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.document_processor import DocumentProcessor
from modules.gemini_analyzer import GeminiSmartAnalyzer
from modules.file_manager import SmartFileManager
from modules.google_integration import GoogleIntegration
from modules.notion_integration import NotionIntegration, NOTION_API_AVAILABLE
from config import SETTINGS

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# 初始化模組（延遲初始化，避免 Flask debug 模式重複載入問題）
processor = None
analyzer = None
file_manager = None
google_integration = None
notion_integration = None

def init_modules():
    """初始化所有模組（僅在主程序中執行一次）"""
    global processor, analyzer, file_manager, google_integration, notion_integration

    if processor is None:
        processor = DocumentProcessor()

    if analyzer is None:
        # 只使用使用者透過 UI 儲存的 API Key
        user_settings = load_user_settings()
        api_key = user_settings.get('gemini_api_key', '')
        analyzer = GeminiSmartAnalyzer(api_key=api_key)

    if file_manager is None:
        file_manager = SmartFileManager()

    if google_integration is None:
        # 完全延遲認證，只有在用戶點擊連線時才進行
        google_integration = GoogleIntegration(auto_auth=False)
        print("Google 整合模組已載入（未連線）")

    if notion_integration is None:
        # 初始化 Notion 整合
        user_settings = load_user_settings()
        notion_token = user_settings.get('notion_api_token', '')
        notion_integration = NotionIntegration(api_token=notion_token)
        # 載入已儲存的資料庫 ID
        if user_settings.get('notion_task_db_id'):
            notion_integration.task_db_id = user_settings.get('notion_task_db_id')
        if user_settings.get('notion_archive_db_id'):
            notion_integration.archive_db_id = user_settings.get('notion_archive_db_id')
        print(f"Notion 整合模組已載入（連線狀態: {notion_integration.is_connected}）")

# 確保模組在首次請求前已初始化
@app.before_request
def ensure_initialized():
    """確保模組已初始化"""
    if processor is None:
        init_modules()

# ===== 使用者設定管理 =====
USER_SETTINGS_FILE = os.path.join(os.path.dirname(__file__), 'user_settings.json')

def load_user_settings():
    """載入使用者設定"""
    if os.path.exists(USER_SETTINGS_FILE):
        try:
            with open(USER_SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    # 預設使用 config.py 的設定
    return {
        'scan_directory': SETTINGS['paths']['scan_directory'],
        'target_directory': SETTINGS['paths']['target_directory']
    }

def save_user_settings(settings):
    """儲存使用者設定"""
    with open(USER_SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

def get_scan_directory():
    """取得掃描目錄（優先使用使用者設定）"""
    user_settings = load_user_settings()
    return user_settings.get('scan_directory', SETTINGS['paths']['scan_directory'])

def get_target_directory():
    """取得歸檔目錄（優先使用使用者設定）"""
    user_settings = load_user_settings()
    return user_settings.get('target_directory', SETTINGS['paths']['target_directory'])

@app.route('/api/connect_google', methods=['POST'])
def connect_google():
    """觸發 Google 認證"""
    try:
        print("="*50)
        print("開始 Google 授權流程...")
        google_integration._authenticate()
        print(f"授權完成，狀態: {google_integration.is_authenticated}")
        print("="*50)
        return jsonify({
            'success': google_integration.is_authenticated,
            'message': '授權成功' if google_integration.is_authenticated else '授權失敗'
        })
    except Exception as e:
        print(f"Google 授權錯誤: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """取得目前設定"""
    settings = load_user_settings()
    # 不回傳完整 API Key，只回傳狀態資訊
    saved_key = settings.get('gemini_api_key', '')
    notion_token = settings.get('notion_api_token', '')
    response = {
        'scan_directory': settings.get('scan_directory', ''),
        'target_directory': settings.get('target_directory', ''),
        'has_saved_api_key': bool(saved_key),
        'api_key_hint': (saved_key[:8] + '***') if saved_key else '',
        'has_session_api_key': bool(analyzer and analyzer.is_available and not saved_key),
        # Notion 設定
        'notion_api_available': NOTION_API_AVAILABLE,
        'has_notion_token': bool(notion_token),
        'notion_token_hint': (notion_token[:8] + '***') if notion_token else '',
        'notion_parent_page_id': settings.get('notion_parent_page_id', ''),
        'notion_task_db_id': settings.get('notion_task_db_id', ''),
        'notion_archive_db_id': settings.get('notion_archive_db_id', ''),
        'notion_connected': notion_integration.is_connected if notion_integration else False,
        'notion_task_db_ready': bool(settings.get('notion_task_db_id')),
        'notion_archive_db_ready': bool(settings.get('notion_archive_db_id'))
    }
    return jsonify(response)

@app.route('/api/settings', methods=['POST'])
def update_settings():
    """儲存使用者設定"""
    global analyzer, notion_integration
    try:
        data = request.json
        settings = load_user_settings()

        if 'scan_directory' in data:
            settings['scan_directory'] = data['scan_directory']
        if 'target_directory' in data:
            settings['target_directory'] = data['target_directory']

        api_key_updated = False
        gemini_available = None
        notion_updated = False

        # 處理 Gemini API Key
        if 'gemini_api_key' in data and data['gemini_api_key']:
            new_key = data['gemini_api_key'].strip()
            save_key = data.get('save_api_key', True)

            # 重新初始化 Gemini analyzer
            analyzer = GeminiSmartAnalyzer(api_key=new_key)
            api_key_updated = True
            gemini_available = analyzer.is_available

            if save_key:
                settings['gemini_api_key'] = new_key
            else:
                # 不儲存：移除已存的 key（如果之前有存）
                settings.pop('gemini_api_key', None)

        # 處理 Notion API Token
        if 'notion_api_token' in data and data['notion_api_token']:
            new_token = data['notion_api_token'].strip()
            settings['notion_api_token'] = new_token
            # 重新連線 Notion
            if notion_integration:
                notion_integration.set_token(new_token)
            else:
                notion_integration = NotionIntegration(api_token=new_token)
            notion_updated = True

        # 處理 Notion 父頁面 ID
        if 'notion_parent_page_id' in data:
            settings['notion_parent_page_id'] = data['notion_parent_page_id'].strip()

        save_user_settings(settings)
        return jsonify({
            'success': True,
            'api_key_updated': api_key_updated,
            'gemini_available': gemini_available,
            'notion_updated': notion_updated,
            'notion_connected': notion_integration.is_connected if notion_integration else False
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/browse', methods=['POST'])
def browse_folder():
    """瀏覽資料夾內容"""
    try:
        data = request.json
        path = data.get('path', '')
        
        # 如果沒有指定路徑，返回可用的磁碟機
        if not path:
            import string
            drives = []
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    drives.append({
                        'name': drive,
                        'path': drive,
                        'is_drive': True
                    })
            return jsonify({'folders': drives, 'current_path': ''})
        
        folder_path = Path(path)
        if not folder_path.exists():
            return jsonify({'error': '路徑不存在'}), 404
            
        folders = []
        try:
            for item in folder_path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    folders.append({
                        'name': item.name,
                        'path': str(item)
                    })
        except PermissionError:
            return jsonify({'error': '無法存取此資料夾'}), 403
            
        folders.sort(key=lambda x: x['name'].lower())
        parent = str(folder_path.parent) if folder_path.parent != folder_path else None
        
        return jsonify({
            'folders': folders,
            'current_path': str(folder_path),
            'parent_path': parent
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/scan')
def scan_docs():
    """掃描目錄中的公文 PDF 檔案（只掃描 _print.pdf 結尾的本文）"""
    import re
    
    scan_path = Path(get_scan_directory())
    if not scan_path.exists():
        return jsonify({'error': f'掃描目錄不存在: {scan_path}'}), 404
    
    # 只掃描 _print.pdf 結尾的公文本文
    print_files = list(scan_path.glob("*_print.pdf"))
    files_list = []
    
    for f in print_files:
        # 取得檔案前綴 (例如: 376480000A_1140300213)
        # 檔名格式: 前綴_print.pdf
        prefix = f.name.rsplit('_print.pdf', 1)[0]
        
        # 尋找對應的附件檔案 (ATTACH1.pdf, ATTACH2.docx, ...)
        attachments = []
        for att_file in scan_path.glob(f"{prefix}_ATTACH*"):
            if not att_file.is_file():
                continue
            # 提取附件編號（支援所有副檔名）
            att_match = re.search(r'_ATTACH(\d+)', att_file.name, re.IGNORECASE)
            att_num = int(att_match.group(1)) if att_match else 0
            attachments.append({
                'name': att_file.name,
                'path': str(att_file),
                'size': att_file.stat().st_size,
                'number': att_num
            })
        
        # 依附件編號排序
        attachments.sort(key=lambda x: x['number'])
        
        files_list.append({
            'name': f.name,
            'path': str(f),
            'size': f.stat().st_size,
            'mtime': f.stat().st_mtime,
            'prefix': prefix,
            'attachments': attachments,
            'attachment_count': len(attachments)
        })
        
    # 依修改時間排序
    files_list.sort(key=lambda x: x['mtime'], reverse=True)
    
    return jsonify({
        'files': files_list,
        'scan_path': str(scan_path),
        'total_documents': len(files_list)
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_doc():
    """分析單一文件"""
    data = request.json
    file_path = data.get('path')
    
    if not file_path or not os.path.exists(file_path):
        return jsonify({'error': '檔案不存在'}), 404
        
    try:
        # 1. 提取內文
        doc_info = processor.process_pdf(file_path)
        if not doc_info:
            return jsonify({'error': '無法提取 PDF 內容'}), 400
            
        # 2. Gemini 分析
        if not analyzer.is_available:
            return jsonify({'error': 'Gemini API 未設定'}), 500
            
        analysis = analyzer.analyze_document(doc_info)
        
        if 'error' in analysis:
            return jsonify({'error': analysis['error']}), 500
            
        return jsonify({
            'doc_info': doc_info,
            'analysis': analysis
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/google/calendar', methods=['POST'])
def create_calendar_event():
    """建立行事曆事件"""
    data = request.json
    analysis = data.get('analysis')

    if not google_integration.is_authenticated:
        return jsonify({'error': 'Google API 未認證'}), 401

    try:
        # 強制設定為行事曆類型
        analysis['google_suggestion']['type'] = 'calendar'

        # 處理自定義日期
        event_date = None
        if 'custom_date' in data:
            from datetime import datetime
            analysis['google_suggestion']['custom_date'] = datetime.fromisoformat(data['custom_date'])
            event_date = data['custom_date']
        else:
            event_date = analysis.get('google_suggestion', {}).get('due_date', '')

        result = google_integration.create_from_analysis(analysis)

        # 如果 Google 建立成功，自動同步到 Notion
        if result.get('success') and notion_integration and notion_integration.is_connected:
            if notion_integration.task_db_id:
                notion_result = notion_integration.add_task_entry(
                    analysis=analysis,
                    event_type='calendar',
                    event_date=result.get('date', event_date)
                )
                result['notion_sync'] = notion_result
                print(f"Notion 同步結果: {notion_result.get('success')}")

        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/google/task', methods=['POST'])
def create_task():
    """建立 Tasks 任務"""
    data = request.json
    analysis = data.get('analysis')

    if not google_integration.is_authenticated:
        return jsonify({'error': 'Google API 未認證'}), 401

    try:
        # 強制設定為 Task 類型
        analysis['google_suggestion']['type'] = 'task'

        # 處理自定義日期
        task_date = None
        if 'custom_date' in data:
            from datetime import datetime
            analysis['google_suggestion']['custom_date'] = datetime.fromisoformat(data['custom_date'])
            task_date = data['custom_date']
        else:
            task_date = analysis.get('google_suggestion', {}).get('due_date', '')

        result = google_integration.create_from_analysis(analysis)

        # 如果 Google 建立成功，自動同步到 Notion
        if result.get('success') and notion_integration and notion_integration.is_connected:
            if notion_integration.task_db_id:
                notion_result = notion_integration.add_task_entry(
                    analysis=analysis,
                    event_type='task',
                    event_date=result.get('due_date', task_date)
                )
                result['notion_sync'] = notion_result
                print(f"Notion 同步結果: {notion_result.get('success')}")

        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/archive', methods=['POST'])
def archive_doc():
    """歸檔文件（包含附件）"""
    data = request.json

    try:
        source_file = data.get('file_path')
        doc_info = data.get('doc_info', {})
        analysis = data.get('analysis')
        google_result = data.get('google_result')
        attachments = data.get('attachments', [])  # 新增：接收附件列表

        # 將附件資訊加入 doc_info
        if attachments:
            doc_info['attachments'] = attachments

        # 允許用戶修改分析結果（例如主旨）後再歸檔
        if 'modified_subject' in data:
            analysis['refined_subject'] = data['modified_subject']

        result = file_manager.organize_document(
            source_file=source_file,
            doc_info=doc_info,
            analysis=analysis,
            google_result=google_result
        )

        # 如果歸檔成功，自動同步到 Notion
        if result.get('success') and notion_integration and notion_integration.is_connected:
            if notion_integration.archive_db_id:
                folder_name = result.get('folder_name', analysis.get('refined_subject', ''))
                archive_path = result.get('target_path', '')
                notion_result = notion_integration.add_archive_entry(
                    analysis=analysis,
                    folder_name=folder_name,
                    archive_path=archive_path
                )
                result['notion_sync'] = notion_result
                print(f"Notion 歸檔同步結果: {notion_result.get('success')}")

        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/notion/connect', methods=['POST'])
def connect_notion():
    """連線 Notion 並建立資料庫"""
    global notion_integration
    try:
        data = request.json
        parent_page_id = data.get('parent_page_id', '').strip()

        if not parent_page_id:
            return jsonify({'success': False, 'error': '請提供父頁面 ID'}), 400

        settings = load_user_settings()
        token = settings.get('notion_api_token', '')

        if not token:
            return jsonify({'success': False, 'error': '請先設定 Notion API Token'}), 400

        # 確保 notion_integration 已初始化
        if notion_integration is None:
            notion_integration = NotionIntegration(api_token=token)
        elif not notion_integration.is_connected:
            notion_integration.set_token(token)

        if not notion_integration.is_connected:
            return jsonify({'success': False, 'error': 'Notion 連線失敗，請確認 API Token 是否正確'}), 400

        # 建立資料庫
        result = notion_integration.create_databases(parent_page_id)

        if result['success']:
            # 儲存資料庫 ID
            settings['notion_parent_page_id'] = parent_page_id
            if result.get('task_db'):
                settings['notion_task_db_id'] = result['task_db']['id']
            if result.get('archive_db'):
                settings['notion_archive_db_id'] = result['archive_db']['id']
            save_user_settings(settings)

        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/notion/status')
def notion_status():
    """取得 Notion 整合狀態"""
    if notion_integration is None:
        return jsonify({
            'available': NOTION_API_AVAILABLE,
            'connected': False,
            'task_db_ready': False,
            'archive_db_ready': False
        })

    status = notion_integration.get_status()
    return jsonify(status)


@app.route('/api/notion/test', methods=['POST'])
def test_notion_connection():
    """測試 Notion 連線"""
    global notion_integration
    try:
        data = request.json
        token = data.get('token', '').strip()

        if not token:
            # 使用已儲存的 token
            settings = load_user_settings()
            token = settings.get('notion_api_token', '')

        if not token:
            return jsonify({'success': False, 'error': '請提供 Notion API Token'}), 400

        # 測試連線
        test_integration = NotionIntegration(api_token=token)
        result = test_integration.test_connection()

        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/status')
def system_status():
    """取得系統狀態"""
    # 確保模組已初始化
    if google_integration is None or analyzer is None:
        init_modules()

    return jsonify({
        'google_auth': google_integration.is_authenticated if google_integration else False,
        'gemini_api': analyzer.is_available if analyzer else False,
        'notion_connected': notion_integration.is_connected if notion_integration else False,
        'notion_task_db_ready': bool(notion_integration.task_db_id) if notion_integration else False,
        'notion_archive_db_ready': bool(notion_integration.archive_db_id) if notion_integration else False,
        'scan_dir': SETTINGS['paths']['scan_directory'],
        'target_dir': SETTINGS['paths']['target_directory']
    })

if __name__ == '__main__':
    # 確保 template 資料夾存在
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # 檢查是否為 Flask reloader 的子程序
    # 如果是主程序（非 reloader 子程序），才進行初始化
    import werkzeug.serving
    is_reloader_process = os.environ.get('WERKZEUG_RUN_MAIN') == 'true'
    
    if not is_reloader_process:
        print("🚀 公文智能處理系統 啟動中...")
        print("=" * 40)
    
    # 初始化模組（僅在真正需要時）
    init_modules()
    
    if not is_reloader_process:
        print("=" * 40)
        print("啟動 Web UI...")
        print("開啟瀏覽器訪問: http://127.0.0.1:5001")
    
    # 使用 use_reloader=False 來避免重複初始化問題
    # 如果你需要自動重載功能，可以改為 use_reloader=True
    app.run(debug=True, port=5001, use_reloader=False)
