"""
SublimeLight - Sidebar Component View
Handles directory operations, folder workspaces, and dynamic file tree listings
fully integrated with a stable multi-tab application context engine.
"""

import os
import customtkinter as ctk
import config
from services.file_service import FileService

class SidebarComponent(ctk.CTkFrame):
    def __init__(self, parent, context):
        super().__init__(parent, width=200, fg_color=config.COLOR_SIDEBAR, corner_radius=0)
        self.context = context
        self.context.sidebar = self  
        self.pack_propagate(False)   
        
        self.current_workspace_folder = None
        self.active_file_buttons = [] 

        # --- Sidebar Actions Layout Assembly ---
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

        # Standalone file tracker indicator element shell (used when no folder project is open)
        self.standalone_file_btn = ctk.CTkButton(
            self, text="", font=(config.FONT_UI, 12),
            fg_color="transparent", text_color=config.COLOR_TEXT,
            hover_color="#2c313c", anchor="w", height=22, command=self._click_standalone_file
        )
        self.standalone_file_path = None 

        # Scrollable workspace tree list layout container
        self.files_scroll_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent", corner_radius=0, label_text=""
        )
        self.files_scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)

    def _trigger_new_file(self):
        """Clears file state contexts to initialize a blank unpersisted document track inside a tab."""
        self.standalone_file_btn.pack_forget()
        self.standalone_file_path = None
        self.context.open_new_tab("untitled", "")

    def _trigger_open_file(self):
        """Loads a standalone individual file selection directly into a new tab container."""
        path, text = FileService.read_file()
        if path is not None:
            self.current_workspace_folder = None
            for btn in self.active_file_buttons:
                btn.destroy()
            self.active_file_buttons.clear()
            
            # Enforce path normalization immediately at load time
            norm_path = os.path.normpath(os.path.abspath(path))
            self.context.open_new_tab(norm_path, text)

    def _trigger_open_folder(self):
        """Scans a selected folder directory and populates file lists onto the sidebar view panel."""
        folder_path, files_list = FileService.scan_folder()
        if not folder_path:
            return
            
        self.standalone_file_btn.pack_forget()
        self.standalone_file_path = None

        self.current_workspace_folder = os.path.normpath(os.path.abspath(folder_path))
        folder_name = os.path.basename(self.current_workspace_folder).upper()
        self.workspace_title_lbl.configure(text=folder_name, text_color="#5c6370")
        
        # ONE-TIME INITIALIZATION SYNC: Force the terminal to jump to the newly opened folder path 
        # immediately upon selection, without creating any automatic background tracking loops later!
        if self.context and self.context.terminal:
            self.context.terminal.sync_workspace_directory(self.current_workspace_folder)
        
        self._build_folder_tree_ui(files_list)

    def _build_folder_tree_ui(self, files_list):
        """Helper to draw file item buttons inside our folder scrolling view."""
        for btn in self.active_file_buttons:
            btn.destroy()
        self.active_file_buttons.clear()

        for file_name in files_list:
            full_file_path = os.path.normpath(os.path.join(self.current_workspace_folder, file_name))
            
            file_btn = ctk.CTkButton(
                self.files_scroll_frame,
                text=f"  📄 {file_name}",
                font=(config.FONT_UI, 12),
                fg_color="transparent",
                text_color=config.COLOR_TEXT,
                hover_color="#2c313c",
                anchor="w",
                height=22,
                command=lambda p=full_file_path: self._load_file_from_sidebar(p)
            )
            file_btn.pack(fill="x", pady=1)
            self.active_file_buttons.append(file_btn)

    def _load_file_from_sidebar(self, file_path):
        """Helper to pull files inside the workspace view panel and route them to multi-tab cache buffers."""
        norm_path = os.path.normpath(os.path.abspath(file_path))
        text = FileService.read_file_from_path(norm_path)
        if text is not None:
            self.context.open_new_tab(norm_path, text)

    def _click_standalone_file(self):
        """Refocuses the standalone tracker file if its link text is clicked in the explorer tree."""
        if self.standalone_file_path:
            self._load_file_from_sidebar(self.standalone_file_path)

    def _trigger_save(self):
        """Extracts text stream from editor and writes it safely onto local hard drive storage."""
        if not self.context.editor:
            return
            
        content = self.context.editor.get_text()
        saved_path = FileService.write_file(self.context.current_file, content)
        
        if saved_path:
            norm_saved_path = os.path.normpath(os.path.abspath(saved_path))
            
            if self.context.current_file == "untitled" and "untitled" in self.context.open_tabs:
                del self.context.open_tabs["untitled"]
                
            self.context.open_tabs[norm_saved_path] = content
            self.context.set_active_file(norm_saved_path)
            
            if self.current_workspace_folder:
                self._refresh_workspace_folder()
            else:
                self.update_file_label(norm_saved_path)

    def _refresh_workspace_folder(self):
        if not self.current_workspace_folder:
            return
        try:
            all_items = os.listdir(self.current_workspace_folder)
            valid_files = [
                f for f in all_items 
                if os.path.isfile(os.path.join(self.current_workspace_folder, f)) and not f.startswith(".")
            ]
            self._build_folder_tree_ui(sorted(valid_files))
        except:
            pass

    def update_file_label(self, path):
        """Triggers dynamically from context manager to track standalone file openings outside of folders."""
        if not self.current_workspace_folder and path and path != "untitled":
            self.workspace_title_lbl.configure(text="STANDALONE FILE", text_color="#4b5263")
            self.standalone_file_path = os.path.normpath(os.path.abspath(path))
            name = os.path.basename(path)
            
            self.standalone_file_btn.configure(text=f"  📄 {name}")
            self.standalone_file_btn.pack(fill="x", padx=5, pady=2, after=self.workspace_title_lbl)
