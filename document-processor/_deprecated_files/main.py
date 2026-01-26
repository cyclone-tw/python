#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公文智能處理系統 v1.0 - 互動式版本
主程式入口 - 使用 Gemini API 進行公文智能分析與處理
"""

import sys
import os
from pathlib import Path

# 設定編碼以支援中文輸出
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# 加入模組路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.document_processor import DocumentProcessor
from modules.gemini_analyzer import GeminiSmartAnalyzer
from modules.file_manager import SmartFileManager
from modules.google_integration import GoogleIntegration
from config import SETTINGS


def display_header():
    """顯示程式標題"""
    print("公文智能處理系統 v1.0")
    print("=" * 50)


def scan_documents():
    """掃描並顯示所有公文"""
    scan_path = Path(SETTINGS['paths']['scan_directory'])
    if not scan_path.exists():
        print(f"❌ 掃描目錄不存在: {scan_path}")
        return []

    pdf_files = list(scan_path.glob("*_print.pdf"))
    if not pdf_files:
        print(f"📁 掃描目錄中沒有找到 *_print.pdf 檔案: {scan_path}")
        return []

    print(f"📄 找到 {len(pdf_files)} 個公文檔案:")
    print("-" * 30)

    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"{i:2d}. {pdf_file.name}")

    return pdf_files


def process_documents(pdf_files):
    """處理並分析所有公文"""
    print("\n🔍 開始分析所有公文...")
    print("=" * 50)

    # 初始化模組
    processor = DocumentProcessor()
    analyzer = GeminiSmartAnalyzer(api_key=SETTINGS['gemini']['api_key'])

    if not analyzer.is_available:
        print("❌ Gemini API 未設定或無法使用，請檢查 config.py")
        return []

    processed_docs = []

    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n📄 處理第 {i}/{len(pdf_files)} 個: {pdf_file.name}")
        print("-" * 40)

        try:
            # 1. 提取PDF內容
            print("   🔍 提取PDF內容...")
            doc_info = processor.process_pdf(str(pdf_file))
            if not doc_info:
                print(f"   ❌ 無法處理PDF: {pdf_file.name}")
                continue

            # 2. Gemini智能分析
            print("   🤖 Gemini AI 分析中...")
            analysis = analyzer.analyze_document(doc_info)
            if 'error' in analysis:
                print(f"   ❌ 分析失敗: {analysis['error']}")
                continue

            # 3. 顯示分析結果
            print("   ✅ 分析完成!")
            print(f"   📝 建議檔名: {analysis.get('suggested_filename', '未知')}")
            print(f"   📋 主旨: {analysis.get('refined_subject', '未知')}")
            print(f"   🗂️  文件類型: {analysis.get('document_type', '未知')}")

            processed_docs.append({
                'file_path': str(pdf_file),
                'doc_info': doc_info,
                'analysis': analysis
            })

        except Exception as e:
            print(f"   ❌ 處理 {pdf_file.name} 時發生錯誤: {e}")
            continue

    print(f"\n✅ 分析完成！成功處理 {len(processed_docs)} 個公文")
    return processed_docs


def google_integration_menu(processed_docs):
    """Google 整合選單"""
    if not processed_docs:
        return

    print("\n📅 Google 整合功能")
    print("=" * 50)

    google_integration = GoogleIntegration()
    if not google_integration.is_authenticated:
        print("❌ Google API 未認證，跳過 Google 整合功能")
        input("按 Enter 繼續...")
        return

    print("請選擇要為哪些公文建立 Google 事件:")
    print("0. 跳過 Google 整合")

    for i, doc in enumerate(processed_docs, 1):
        subject = doc['analysis'].get('refined_subject', '未知')
        print(f"{i}. {subject}")

    print(f"{len(processed_docs) + 1}. 全部建立")

    while True:
        try:
            choice = input(f"\n請選擇 (0-{len(processed_docs) + 1}): ").strip()

            if choice == '0':
                print("⏭️ 跳過 Google 整合")
                break
            elif choice == str(len(processed_docs) + 1):
                # 全部建立
                for doc in processed_docs:
                    create_google_event(google_integration, doc)
                break
            elif choice.isdigit() and 1 <= int(choice) <= len(processed_docs):
                # 建立單一事件
                doc = processed_docs[int(choice) - 1]
                create_google_event(google_integration, doc)
                break
            else:
                print("❌ 無效選擇，請重新輸入")
        except (ValueError, KeyboardInterrupt):
            print("❌ 無效輸入，請重新輸入")


def create_google_event(google_integration, doc):
    """建立單一 Google 事件"""
    analysis = doc['analysis']
    subject = analysis.get('refined_subject', '未知')

    print(f"\n📅 為「{subject}」建立 Google 事件")
    print("=" * 60)

    # 顯示分析摘要
    display_analysis_summary(analysis)

    # 取得AI建議
    google_suggestion = analysis.get('google_suggestion', {})
    suggested_type = google_suggestion.get('type', 'task')
    suggested_reason = google_suggestion.get('reason', '無建議原因')

    print(f"\n🤖 AI 建議: {suggested_type} - {suggested_reason}")

    # 讓用戶選擇
    print("\n請選擇操作:")
    print("1. 建立行事曆事件")
    print("2. 建立 Tasks 任務")
    print("3. 跳過")

    while True:
        try:
            choice = input("請選擇 (1-3): ").strip()

            if choice == '1':
                # 建立行事曆事件
                google_result = create_calendar_event_with_confirmation(google_integration, analysis)
                if google_result:
                    print(f"   ✅ 行事曆事件建立完成")
                    doc['google_result'] = google_result
                break
            elif choice == '2':
                # 建立 Tasks 任務
                google_result = create_task_with_confirmation(google_integration, analysis)
                if google_result:
                    print(f"   ✅ Tasks 任務建立完成")
                    doc['google_result'] = google_result
                break
            elif choice == '3':
                print(f"   ⏭️ 跳過「{subject}」")
                break
            else:
                print("❌ 無效選擇，請重新輸入")
        except (ValueError, KeyboardInterrupt):
            print("❌ 無效輸入，請重新輸入")


def display_analysis_summary(analysis):
    """顯示分析摘要"""
    print("\n📋 公文分析摘要:")
    print("-" * 40)
    print(f"主旨: {analysis.get('refined_subject', '未知')}")
    print(f"文件類型: {analysis.get('document_type', '未知')}")
    print(f"重要性: {analysis.get('priority', '未知')}")

    # 顯示重要日期
    important_dates = analysis.get('important_dates', [])
    if important_dates:
        print(f"\n📅 重要日期:")
        for date_info in important_dates:
            date = date_info.get('date', '')
            desc = date_info.get('description', '')
            print(f"  • {date}: {desc}")
    else:
        print(f"\n📅 重要日期: 無識別到明確日期")

    # 顯示行動項目
    action_items = analysis.get('action_items', [])
    if action_items:
        print(f"\n📝 行動項目:")
        for action in action_items:
            desc = action.get('description', '')
            deadline = action.get('deadline', '')
            print(f"  • {desc} {f'(截止: {deadline})' if deadline else ''}")

    # 顯示聯絡資訊
    contact = analysis.get('contact_info', {})
    if contact and contact.get('name'):
        print(f"\n👤 聯絡人: {contact.get('name', '')} {contact.get('phone', '')} {contact.get('email', '')}")


def create_calendar_event_with_confirmation(google_integration, analysis):
    """建立行事曆事件，包含確認步驟"""
    print(f"\n📅 建立行事曆事件")

    # 1. 確認標題
    suggested_title = analysis.get('refined_subject', '公文事件')
    print(f"事件標題: {suggested_title}")

    # 2. 解析並確認日期
    event_date = get_event_date_from_user(analysis)
    if not event_date:
        print("   ❌ 未指定日期，取消建立事件")
        return None

    # 3. 最終確認
    print(f"\n✅ 即將建立行事曆事件:")
    print(f"   標題: {suggested_title}")
    print(f"   日期: {event_date.strftime('%Y年%m月%d日 %H:%M')}")

    confirm = input("確認建立? (y/N): ").strip().lower()
    if confirm != 'y':
        print("   ❌ 已取消")
        return None

    # 4. 建立事件
    try:
        analysis['google_suggestion']['type'] = 'calendar'
        analysis['google_suggestion']['custom_date'] = event_date
        result = google_integration.create_from_analysis(analysis)

        if result['success']:
            print(f"   ✅ 成功: {result.get('title', '')}")
            return result
        else:
            print(f"   ❌ 失敗: {result.get('error', '')}")
            return result
    except Exception as e:
        print(f"   ❌ 建立失敗: {e}")
        return {'success': False, 'error': str(e), 'type': 'calendar'}


def create_task_with_confirmation(google_integration, analysis):
    """建立 Tasks 任務，包含確認步驟"""
    print(f"\n📋 建立 Tasks 任務")

    # 1. 確認標題
    suggested_title = analysis.get('refined_subject', '公文處理')
    print(f"任務標題: {suggested_title}")

    # 2. 解析並確認截止日期
    due_date = get_due_date_from_user(analysis)

    # 3. 最終確認
    print(f"\n✅ 即將建立 Tasks 任務:")
    print(f"   標題: {suggested_title}")
    if due_date:
        print(f"   截止日期: {due_date.strftime('%Y年%m月%d日')}")
    else:
        print(f"   截止日期: 未設定")

    confirm = input("確認建立? (y/N): ").strip().lower()
    if confirm != 'y':
        print("   ❌ 已取消")
        return None

    # 4. 建立任務
    try:
        analysis['google_suggestion']['type'] = 'task'
        if due_date:
            analysis['google_suggestion']['custom_date'] = due_date
        result = google_integration.create_from_analysis(analysis)

        if result['success']:
            print(f"   ✅ 成功: {result.get('title', '')}")
            return result
        else:
            print(f"   ❌ 失敗: {result.get('error', '')}")
            return result
    except Exception as e:
        print(f"   ❌ 建立失敗: {e}")
        return {'success': False, 'error': str(e), 'type': 'task'}


def get_event_date_from_user(analysis):
    """從用戶取得事件日期"""
    from datetime import datetime, timedelta

    # 嘗試從分析結果中提取日期
    suggested_dates = analysis.get('important_dates', [])

    print(f"\n⏰ 請設定事件日期:")

    if suggested_dates:
        print("識別到的日期:")
        for i, date_info in enumerate(suggested_dates, 1):
            date = date_info.get('date', '')
            desc = date_info.get('description', '')
            print(f"  {i}. {date} - {desc}")
        print(f"  {len(suggested_dates) + 1}. 手動輸入日期")
        print(f"  0. 取消")

        while True:
            try:
                choice = input(f"請選擇 (0-{len(suggested_dates) + 1}): ").strip()

                if choice == '0':
                    return None
                elif choice == str(len(suggested_dates) + 1):
                    return input_custom_date()
                elif choice.isdigit() and 1 <= int(choice) <= len(suggested_dates):
                    # 選擇建議的日期
                    selected_date = suggested_dates[int(choice) - 1]
                    return parse_date_string(selected_date.get('date', ''))
                else:
                    print("❌ 無效選擇，請重新輸入")
            except (ValueError, KeyboardInterrupt):
                print("❌ 無效輸入，請重新輸入")
    else:
        print("未識別到明確日期")
        return input_custom_date()


def get_due_date_from_user(analysis):
    """從用戶取得截止日期"""
    # 類似 get_event_date_from_user，但針對 Tasks
    return get_event_date_from_user(analysis)


def input_custom_date():
    """讓用戶手動輸入日期"""
    from datetime import datetime

    print("\n請輸入日期 (格式: YYYY-MM-DD 或 YYYY-MM-DD HH:MM):")
    print("例如: 2024-09-25 或 2024-09-25 14:30")

    while True:
        try:
            date_input = input("日期: ").strip()
            if not date_input:
                return None

            # 嘗試解析日期
            if ' ' in date_input:
                # 包含時間
                return datetime.strptime(date_input, '%Y-%m-%d %H:%M')
            else:
                # 只有日期，設定為上午9點
                return datetime.strptime(date_input + ' 09:00', '%Y-%m-%d %H:%M')

        except ValueError:
            print("❌ 日期格式錯誤，請重新輸入")
        except KeyboardInterrupt:
            return None


def parse_date_string(date_str):
    """解析日期字串"""
    from datetime import datetime
    import re

    if not date_str:
        return None

    try:
        # 民國年格式: 114年9月15日
        roc_match = re.search(r'(\d{2,3})年(\d{1,2})月(\d{1,2})日', date_str)
        if roc_match:
            year = int(roc_match.group(1)) + 1911
            month = int(roc_match.group(2))
            day = int(roc_match.group(3))
            return datetime(year, month, day, 9, 0)

        # 西元年格式: 2024-12-15
        western_match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', date_str)
        if western_match:
            year = int(western_match.group(1))
            month = int(western_match.group(2))
            day = int(western_match.group(3))
            return datetime(year, month, day, 9, 0)

    except (ValueError, AttributeError):
        pass

    return None


def archive_documents(processed_docs):
    """歸檔公文到智能歸檔資料夾"""
    if not processed_docs:
        return

    print("\n📁 歸檔公文到智能歸檔資料夾")
    print("=" * 50)

    file_manager = SmartFileManager()

    print("請選擇要歸檔的公文:")
    print("0. 跳過歸檔")

    for i, doc in enumerate(processed_docs, 1):
        subject = doc['analysis'].get('refined_subject', '未知')
        print(f"{i}. {subject}")

    print(f"{len(processed_docs) + 1}. 全部歸檔")

    while True:
        try:
            choice = input(f"\n請選擇 (0-{len(processed_docs) + 1}): ").strip()

            if choice == '0':
                print("⏭️ 跳過歸檔")
                break
            elif choice == str(len(processed_docs) + 1):
                # 全部歸檔
                print("\n🚀 開始歸檔所有公文...")
                for i, doc in enumerate(processed_docs, 1):
                    print(f"\n📁 歸檔第 {i}/{len(processed_docs)} 個公文")
                    archive_single_document(file_manager, doc)
                print("\n🎉 所有公文歸檔完成！")
                break
            elif choice.isdigit() and 1 <= int(choice) <= len(processed_docs):
                # 歸檔單一公文
                doc = processed_docs[int(choice) - 1]
                archive_single_document(file_manager, doc)
                break
            else:
                print("❌ 無效選擇，請重新輸入")
        except (ValueError, KeyboardInterrupt):
            print("❌ 無效輸入，請重新輸入")


def archive_single_document(file_manager, doc):
    """歸檔單一公文"""
    try:
        # 取得 Google 整合結果（如果有的話）
        google_result = doc.get('google_result', None)

        result = file_manager.organize_document(
            source_file=doc['file_path'],
            doc_info=doc['doc_info'],
            analysis=doc['analysis'],
            google_result=google_result
        )

        if result['success']:
            print(f"   ✅ 歸檔成功: {os.path.basename(result['target_path'])}")
            if result['attachments']:
                print(f"   📎 附件數量: {len(result['attachments'])}")
            if google_result:
                print(f"   📋 Google 整合記錄已包含在處理記錄中")
        else:
            print(f"   ❌ 歸檔失敗: {result['error']}")

    except Exception as e:
        print(f"   ❌ 歸檔時發生錯誤: {e}")


def main():
    """主程式流程"""
    display_header()

    # 步驟1: 掃描公文
    pdf_files = scan_documents()
    if not pdf_files:
        return

    input("\n按 Enter 開始分析公文...")

    # 步驟2: 處理並分析公文
    processed_docs = process_documents(pdf_files)
    if not processed_docs:
        print("❌ 沒有成功處理任何公文")
        return

    input("\n按 Enter 繼續到 Google 整合...")

    # 步驟3: Google 整合
    google_integration_menu(processed_docs)

    input("\n按 Enter 繼續到歸檔...")

    # 步驟4: 歸檔公文
    archive_documents(processed_docs)

    print("\n🎉 所有處理完成！")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程式已中止")
    except Exception as e:
        print(f"\n程式發生錯誤: {e}")
        import traceback
        traceback.print_exc()