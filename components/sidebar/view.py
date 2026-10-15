"""
SublimeLight - Sidebar Component View (Premium Monokai ttk.Treeview)
Handles nested folder explorer hierarchies utilizing a heavily restyled
native Treeview to deliver a sleek, modern, VS Code-inspired dark aesthetic.
"""

import os
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import config
from services.file_service import FileService
from .theme_style import SidebarThemeStyle
from .tree_manager import SidebarTreeManager
from .tree_events import SidebarTreeEvents

# FIXED CLASS NAME: Must exactly match 'SidebarComponent' to satisfy the main.py import pass!
class SidebarComponent(ctk.CTkFrame):
    def __init__(self, parent, context):
        super().__init__(parent, width=200, fg_color=config.COLOR_SIDEBAR, corner_radius=0)
        self.context = context
        self.context.sidebar = self  
        self.pack_propagate(False)   
        
        self.current_workspace_folder = None

        # --- Sidebar Actions Header Assembly ---
        self.folders_label = ctk.CTkLabel(
            self, text="WORKSPACE EXPLORER", font=(config.FONT_UI, 10, "bold"), 
            text_color="#5c6370", anchor="w"
        )
        self.folders_label.pack(fill="x", padx=15, pady=(15, 5))
        
        self.workspace_title_lbl = ctk.CTkLabel(
            self, text="NO WORKSPACE OPEN", font=(config.FONT_UI, 11, "bold"),
            text_color="#4b5263", anchor="w"
        )
        self.workspace_title_lbl.pack(fill="x", padx=15, pady=(10, 5))

        self.standalone_file_btn = ctk.CTkButton(
            self, text="", font=(config.FONT_UI, 12),
            fg_color="transparent", text_color=config.COLOR_TEXT,
            hover_color="#2c313c", anchor="w", height=22, command=self._click_standalone_file
        )
        self.standalone_file_path = None 

        # --- INITIALIZE REFRACTORED CONTAINER NETWORKS ---
        self.tree_container = tk.Frame(self, bg=config.COLOR_SIDEBAR)
        self.tree_container.pack(fill="both", expand=True, padx=5, pady=5)

        # 1. Apply Deep Monokai Look and Feel
        self.theme_style = SidebarThemeStyle.apply_monokai_theme()

        # 2. Instantiate Base Treeview Control
        self.tree = ttk.Treeview(self.tree_container, show="tree", style="Sidebar.Treeview")
        self.tree.column("#0", stretch=True, anchor="w")

        # 3. Mount Native Scrollbar Channels
        self.scrollbar = ttk.Scrollbar(self.tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        # 4. Instantiate Split Architecture Classes
        self.manager = SidebarTreeManager(self.tree)
        self.events = SidebarTreeEvents(self.tree, self.manager, self.context)

        # 5. Connect UI Input Triggers Safely
        self.tree.bind("<<TreeviewOpen>>", self.events.handle_folder_expand)
        self.tree.bind("<<TreeviewClose>>", self.events.handle_folder_collapse)
        self.tree.bind("<Double-1>", self.events.handle_item_double_click)
        self.tree.bind("<Button-1>", self.events.handle_single_click_select)

    def _trigger_open_folder(self):
        folder_path = ctk.filedialog.askdirectory(mustexist=True)
        if not folder_path:
            return
            
        self.standalone_file_btn.pack_forget()
        self.standalone_file_path = None

        self.current_workspace_folder = os.path.normpath(os.path.abspath(folder_path))
        folder_name = os.path.basename(self.current_workspace_folder).upper()
        self.workspace_title_lbl.configure(text=folder_name, text_color="#5c6370")
        
        if self.context and self.context.terminal:
            self.context.terminal.sync_workspace_directory(self.current_workspace_folder)
        
        self.refresh_workspace_tree()

    def refresh_workspace_tree(self):
        if self.current_workspace_folder:
            self.manager.insert_root_folder(self.current_workspace_folder)

    def _click_standalone_file(self):
        if self.standalone_file_path:
            norm_path = os.path.normpath(os.path.abspath(self.standalone_file_path))
            text = FileService.read_file_from_path(norm_path)
            if text is not None:
                self.context.open_new_tab(norm_path, text)

    def _trigger_new_file(self):
        self.standalone_file_btn.pack_forget()
        self.standalone_file_path = None
        self.context.open_new_tab("untitled", "")

    def _trigger_open_file(self):
        path, text = FileService.read_file()
        if path is not None:
            self.current_workspace_folder = None
            self.manager.reset_tree()
            self.context.open_new_tab(os.path.normpath(os.path.abspath(path)), text)

    def _trigger_save(self):
        if not self.context.editor: 
            return
        content = self.context.editor.get_text()
        saved_path = FileService.write_file(self.context.current_file, content)
        if saved_path:
            norm_path = os.path.normpath(os.path.abspath(saved_path))
            if self.context.current_file == "untitled" and "untitled" in self.context.open_tabs:
                del self.context.open_tabs["untitled"]
            self.context.open_tabs[norm_path] = content
            self.context.set_active_file(norm_path)
            if self.current_workspace_folder: 
                self.refresh_workspace_tree()
            else: 
                self.update_file_label(norm_path)

    def _refresh_workspace_folder(self):
        if self.current_workspace_folder: 
            self.refresh_workspace_tree()

    def update_file_label(self, path):
        if not self.current_workspace_folder and path and path != "untitled":
            self.workspace_title_lbl.configure(text="STANDALONE FILE", text_color="#4b5263")
            self.standalone_file_path = os.path.normpath(os.path.abspath(path))
            self.standalone_file_btn.configure(text=f"  📄 {os.path.basename(path)}")
            self.standalone_file_btn.pack(fill="x", padx=5, pady=2, after=self.workspace_title_lbl)
