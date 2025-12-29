#!/usr/bin/env python3
"""
多重工作區管理器 (Multi-Workspace Manager)
Material Design 風格的視覺化工作區切換工具
"""

import customtkinter as ctk
import json
import subprocess
import webbrowser
from pathlib import Path
from typing import Dict, List, Any, Optional


# ═══════════════════════════════════════════════════════════════════════════════
# 設計系統 (Design System) - Material Design Colors
# ═══════════════════════════════════════════════════════════════════════════════

class Colors:
    """Material Design 配色方案"""
    # Primary
    PRIMARY = "#1976D2"
    PRIMARY_DARK = "#1565C0"
    PRIMARY_LIGHT = "#42A5F5"
    
    # Secondary
    SECONDARY = "#9C27B0"
    SECONDARY_DARK = "#7B1FA2"
    
    # Background & Surface
    BACKGROUND = "#121212"
    SURFACE = "#1E1E1E"
    SURFACE_VARIANT = "#2D2D2D"
    
    # Text
    ON_PRIMARY = "#FFFFFF"
    ON_SURFACE = "#FFFFFF"
    ON_SURFACE_VARIANT = "#B3B3B3"
    
    # Semantic
    SUCCESS = "#4CAF50"
    WARNING = "#FF9800"
    ERROR = "#F44336"
    
    # Card elevation
    CARD_SHADOW = "#000000"


class Fonts:
    """字體設定"""
    TITLE = ("SF Pro Display", 28, "bold")
    HEADING = ("SF Pro Display", 18, "bold")
    BODY = ("SF Pro Text", 14)
    BUTTON = ("SF Pro Text", 14, "bold")
    SMALL = ("SF Pro Text", 12)


# ═══════════════════════════════════════════════════════════════════════════════
# 工作區管理器 (Workspace Manager)
# ═══════════════════════════════════════════════════════════════════════════════

class WorkspaceCard(ctk.CTkFrame):
    """單一工作區卡片元件"""
    
    def __init__(
        self, 
        master, 
        name: str, 
        data: Dict[str, List[str]], 
        on_launch: callable,
        on_edit: callable,
        on_delete: callable,
        **kwargs
    ):
        super().__init__(
            master, 
            fg_color=Colors.SURFACE,
            corner_radius=12,
            **kwargs
        )
        
        self.name = name
        self.data = data
        
        # 計算項目數量
        folder_count = len(data.get("folders", []))
        file_count = len(data.get("files", []))
        url_count = len(data.get("urls", []))
        
        # 左側：工作區資訊
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=20, pady=15)
        
        # 工作區名稱
        name_label = ctk.CTkLabel(
            info_frame,
            text=name,
            font=Fonts.HEADING,
            text_color=Colors.ON_SURFACE,
            anchor="w"
        )
        name_label.pack(anchor="w")
        
        # 項目統計
        stats_text = f"📁 {folder_count}  📄 {file_count}  🔗 {url_count}"
        stats_label = ctk.CTkLabel(
            info_frame,
            text=stats_text,
            font=Fonts.SMALL,
            text_color=Colors.ON_SURFACE_VARIANT,
            anchor="w"
        )
        stats_label.pack(anchor="w", pady=(5, 0))
        
        # 右側：操作按鈕
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(side="right", padx=15, pady=15)
        
        # 啟動按鈕
        launch_btn = ctk.CTkButton(
            button_frame,
            text="🚀 啟動",
            font=Fonts.BUTTON,
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_DARK,
            text_color=Colors.ON_PRIMARY,
            corner_radius=8,
            width=100,
            height=36,
            command=lambda: on_launch(name)
        )
        launch_btn.pack(side="left", padx=5)
        
        # 編輯按鈕
        edit_btn = ctk.CTkButton(
            button_frame,
            text="✏️",
            font=Fonts.BUTTON,
            fg_color=Colors.SURFACE_VARIANT,
            hover_color=Colors.SECONDARY_DARK,
            text_color=Colors.ON_SURFACE,
            corner_radius=8,
            width=40,
            height=36,
            command=lambda: on_edit(name)
        )
        edit_btn.pack(side="left", padx=5)
        
        # 刪除按鈕
        delete_btn = ctk.CTkButton(
            button_frame,
            text="🗑️",
            font=Fonts.BUTTON,
            fg_color=Colors.SURFACE_VARIANT,
            hover_color=Colors.ERROR,
            text_color=Colors.ON_SURFACE,
            corner_radius=8,
            width=40,
            height=36,
            command=lambda: on_delete(name)
        )
        delete_btn.pack(side="left", padx=5)


class EditDialog(ctk.CTkToplevel):
    """編輯工作區對話框"""
    
    def __init__(
        self, 
        master, 
        title: str = "新增工作區",
        name: str = "",
        data: Optional[Dict[str, List[str]]] = None,
        on_save: Optional[callable] = None
    ):
        super().__init__(master)
        
        self.on_save = on_save
        self.original_name = name
        
        # 視窗設定 - 增加高度以容納所有元素
        self.title(title)
        self.geometry("650x700")
        self.configure(fg_color=Colors.BACKGROUND)
        self.resizable(True, True)
        self.minsize(500, 500)
        
        # 置中顯示
        self.transient(master)
        self.grab_set()
        
        # 初始化資料
        if data is None:
            data = {"folders": [], "files": [], "urls": []}
        
        self.create_ui(name, data)
        
    def create_ui(self, name: str, data: Dict[str, List[str]]):
        """建立編輯介面"""
        
        # ═══ 頂部：工作區名稱 (固定) ═══
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=30, pady=(25, 10))
        
        name_label = ctk.CTkLabel(
            top_frame,
            text="工作區名稱",
            font=Fonts.BODY,
            text_color=Colors.ON_SURFACE_VARIANT
        )
        name_label.pack(anchor="w")
        
        self.name_entry = ctk.CTkEntry(
            top_frame,
            font=Fonts.BODY,
            fg_color=Colors.SURFACE,
            border_color=Colors.PRIMARY,
            text_color=Colors.ON_SURFACE,
            height=40,
            corner_radius=8
        )
        self.name_entry.pack(fill="x", pady=(5, 0))
        self.name_entry.insert(0, name)
        
        # ═══ 中間：可滾動內容區 ═══
        scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=Colors.SURFACE_VARIANT,
            scrollbar_button_hover_color=Colors.PRIMARY
        )
        scroll_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        # 資料夾路徑
        self._create_textbox_section(scroll_frame, "📁 資料夾", data.get("folders", []), "folders")
        
        # 檔案路徑
        self._create_textbox_section(scroll_frame, "📄 檔案", data.get("files", []), "files")
        
        # 網址
        self._create_textbox_section(scroll_frame, "🔗 網址", data.get("urls", []), "urls")
        
        # ═══ 底部：按鈕區 (固定) ═══
        button_frame = ctk.CTkFrame(self, fg_color=Colors.SURFACE, corner_radius=0, height=70)
        button_frame.pack(fill="x", side="bottom")
        button_frame.pack_propagate(False)
        
        button_container = ctk.CTkFrame(button_frame, fg_color="transparent")
        button_container.pack(expand=True)
        
        save_btn = ctk.CTkButton(
            button_container,
            text="💾 儲存",
            font=Fonts.BUTTON,
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_DARK,
            text_color=Colors.ON_PRIMARY,
            corner_radius=8,
            width=140,
            height=44,
            command=self._save
        )
        save_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(
            button_container,
            text="取消",
            font=Fonts.BUTTON,
            fg_color=Colors.SURFACE_VARIANT,
            hover_color=Colors.ERROR,
            text_color=Colors.ON_SURFACE,
            corner_radius=8,
            width=120,
            height=44,
            command=self.destroy
        )
        cancel_btn.pack(side="left", padx=10)
    
    def _create_textbox_section(
        self, 
        parent, 
        label: str, 
        items: List[str], 
        key: str
    ):
        """建立多行文字輸入區塊"""
        
        section_frame = ctk.CTkFrame(parent, fg_color="transparent")
        section_frame.pack(fill="x", pady=(15, 5))
        
        label_widget = ctk.CTkLabel(
            section_frame,
            text=label,
            font=Fonts.BODY,
            text_color=Colors.ON_SURFACE_VARIANT
        )
        label_widget.pack(anchor="w")
        
        # 使用 CTkTextbox 支援多行輸入
        textbox = ctk.CTkTextbox(
            section_frame,
            font=Fonts.SMALL,
            fg_color=Colors.SURFACE,
            border_color=Colors.SURFACE_VARIANT,
            text_color=Colors.ON_SURFACE,
            border_width=1,
            height=100,
            corner_radius=8
        )
        textbox.pack(fill="x", pady=(5, 0))
        textbox.insert("1.0", "\n".join(items))
        
        # 儲存參考
        setattr(self, f"{key}_textbox", textbox)
    
    def _save(self):
        """儲存工作區"""
        name = self.name_entry.get().strip()
        
        if not name:
            return
        
        # 從 textbox 取得內容
        folders_text = self.folders_textbox.get("1.0", "end-1c")
        files_text = self.files_textbox.get("1.0", "end-1c")
        urls_text = self.urls_textbox.get("1.0", "end-1c")
        
        data = {
            "folders": [p.strip() for p in folders_text.split("\n") if p.strip()],
            "files": [p.strip() for p in files_text.split("\n") if p.strip()],
            "urls": [p.strip() for p in urls_text.split("\n") if p.strip()]
        }
        
        if self.on_save:
            self.on_save(self.original_name, name, data)
        
        self.destroy()



class WorkspaceApp(ctk.CTk):
    """主應用程式"""
    
    def __init__(self):
        super().__init__()
        
        # 視窗設定
        self.title("🗂️ 工作區管理器")
        self.geometry("800x600")
        self.configure(fg_color=Colors.BACKGROUND)
        
        # 設定 CustomTkinter 主題
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # 設定檔路徑
        self.config_path = Path(__file__).parent / "workspaces.json"
        
        # 載入工作區
        self.load_workspaces()
        
        # 建立 UI
        self.create_ui()
    
    def load_workspaces(self):
        """載入工作區設定"""
        if not self.config_path.exists():
            # 建立預設設定
            self.workspaces = {
                "範例工作區": {
                    "folders": [str(Path.home() / "Documents")],
                    "files": [],
                    "urls": ["https://google.com"]
                }
            }
            self.save_workspaces()
        else:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.workspaces = json.load(f)
    
    def save_workspaces(self):
        """儲存工作區設定"""
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.workspaces, f, indent=2, ensure_ascii=False)
    
    def create_ui(self):
        """建立主介面"""
        # 清除現有元件
        for widget in self.winfo_children():
            widget.destroy()
        
        # 標題區
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=40, pady=(30, 20))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="🗂️ 工作區管理器",
            font=Fonts.TITLE,
            text_color=Colors.ON_SURFACE
        )
        title_label.pack(side="left")
        
        # 新增按鈕
        add_btn = ctk.CTkButton(
            header_frame,
            text="➕ 新增工作區",
            font=Fonts.BUTTON,
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_DARK,
            text_color=Colors.ON_PRIMARY,
            corner_radius=8,
            width=140,
            height=40,
            command=self.add_workspace
        )
        add_btn.pack(side="right")
        
        # 分隔線
        separator = ctk.CTkFrame(self, fg_color=Colors.SURFACE_VARIANT, height=1)
        separator.pack(fill="x", padx=40, pady=10)
        
        # 可滾動工作區列表
        scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=Colors.SURFACE_VARIANT,
            scrollbar_button_hover_color=Colors.PRIMARY
        )
        scroll_frame.pack(fill="both", expand=True, padx=40, pady=(10, 30))
        
        # 動態生成工作區卡片
        if not self.workspaces:
            empty_label = ctk.CTkLabel(
                scroll_frame,
                text="尚無工作區\n點擊上方按鈕新增",
                font=Fonts.BODY,
                text_color=Colors.ON_SURFACE_VARIANT
            )
            empty_label.pack(expand=True, pady=100)
        else:
            for name, data in self.workspaces.items():
                card = WorkspaceCard(
                    scroll_frame,
                    name=name,
                    data=data,
                    on_launch=self.launch_workspace,
                    on_edit=self.edit_workspace,
                    on_delete=self.delete_workspace
                )
                card.pack(fill="x", pady=8)
    
    def launch_workspace(self, name: str):
        """啟動工作區"""
        data = self.workspaces.get(name, {})
        
        # 開啟資料夾
        for folder in data.get("folders", []):
            path = Path(folder)
            if path.exists():
                subprocess.run(["open", str(path)])
            else:
                print(f"⚠️ 資料夾不存在: {folder}")
        
        # 開啟檔案
        for file in data.get("files", []):
            path = Path(file)
            if path.exists():
                subprocess.run(["open", str(path)])
            else:
                print(f"⚠️ 檔案不存在: {file}")
        
        # 開啟網址
        for url in data.get("urls", []):
            webbrowser.open(url)
    
    def add_workspace(self):
        """新增工作區"""
        EditDialog(
            self,
            title="新增工作區",
            on_save=self._on_workspace_saved
        )
    
    def edit_workspace(self, name: str):
        """編輯工作區"""
        data = self.workspaces.get(name, {})
        EditDialog(
            self,
            title=f"編輯: {name}",
            name=name,
            data=data,
            on_save=self._on_workspace_saved
        )
    
    def delete_workspace(self, name: str):
        """刪除工作區"""
        if name in self.workspaces:
            del self.workspaces[name]
            self.save_workspaces()
            self.create_ui()
    
    def _on_workspace_saved(self, original_name: str, new_name: str, data: Dict):
        """工作區儲存回調"""
        # 如果名稱變更，先刪除舊的
        if original_name and original_name != new_name:
            if original_name in self.workspaces:
                del self.workspaces[original_name]
        
        # 儲存新的
        self.workspaces[new_name] = data
        self.save_workspaces()
        self.create_ui()


# ═══════════════════════════════════════════════════════════════════════════════
# 程式入口
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = WorkspaceApp()
    app.mainloop()
