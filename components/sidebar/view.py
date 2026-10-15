"""
SublimeLight - Sidebar Component View
Handles directory operations, folder workspaces, and orchestrates decentralized sub-modules.
"""

import os
import customtkinter as ctk
import config
from services.file_service import FileService
from .tree_builder import TreeBuilder
from .tree_node import TreeNodeButton

class SidebarComponent(ctk.CTkFrame):
    def __init__(self, parent, context):
        super().__init__(parent, width=200, fg_color=config.COLOR_SIDEBAR, corner_radius=0)
        self.context = context
        self.context.sidebar = self  
        self.pack_propagate(False)   
        
        self.current_workspace_folder = None
        self.active_tree_widgets = [] 
        self.expanded_folders = set() 

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
        self.standalone_file_btn.pack_forget()
        self.standalone_file_path = None
        self.context.open_new_tab("untitled", "")

    def _trigger_open_file(self):
        path, text = FileService.read_file()
        if path is not None:
            self.current_workspace_folder = None
            self._clear_tree_widgets()
            norm_path = os.path.normpath(os.path.abspath(path))
            self.context.open_new_tab(norm_path, text)

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
        
        self.expanded_folders.add(self.current_workspace_folder)
        self.refresh_workspace_tree()

    def _clear_tree_widgets(self):
        for widget in self.active_tree_widgets:
            widget.destroy()
        self.active_tree_widgets.clear()

    def refresh_workspace_tree(self):
        if not self.current_workspace_folder:
            return
        self._clear_tree_widgets()
        self._render_directory_level(self.current_workspace_folder, indent_level=0)
        self.files_scroll_frame.update_idletasks()

    def _render_directory_level(self, target_dir, indent_level):
        """Delegates path processing up onto specialized modules and mounts nodes cleanly inside the canvas view."""
        folders, files = TreeBuilder.scan_and_sort_directory(target_dir)

        # 1. MOUNT SORTED SUB-FOLDERS
        for name, full_path in folders:
            is_expanded = full_path in self.expanded_folders
            
            # STANDARD PASSTHROUGH: Pass self.files_scroll_frame directly as master parent
            folder_node = TreeNodeButton(
                master=self.files_scroll_frame,
                name=name, full_path=full_path,
                is_folder=True, is_expanded=is_expanded,
                indent_level=indent_level,
                toggle_cmd=self._toggle_folder_state,
                load_cmd=self._load_file_from_sidebar,
                scroll_frame=self.files_scroll_frame
            )
            self.active_tree_widgets.append(folder_node)

            if is_expanded:
                self._render_directory_level(full_path, indent_level + 1)

        # 2. MOUNT SORTED FILES
        for name, full_path in files:
            # STANDARD PASSTHROUGH: Pass self.files_scroll_frame directly as master parent
            file_node = TreeNodeButton(
                master=self.files_scroll_frame,
                name=name, full_path=full_path,
                is_folder=False, is_expanded=False,
                indent_level=indent_level,
                toggle_cmd=self._toggle_folder_state,
                load_cmd=self._load_file_from_sidebar,
                scroll_frame=self.files_scroll_frame
            )
            self.active_tree_widgets.append(file_node)

    def _toggle_folder_state(self, folder_path):
        if folder_path in self.expanded_folders:
            self.expanded_folders.remove(folder_path)
        else:
            self.expanded_folders.add(folder_path)
        self.refresh_workspace_tree()

    def _load_file_from_sidebar(self, file_path):
        norm_path = os.path.normpath(os.path.abspath(file_path))
        text = FileService.read_file_from_path(norm_path)
        if text is not None:
            self.context.open_new_tab(norm_path, text)

    def _click_standalone_file(self):
        if self.standalone_file_path:
            self._load_file_from_sidebar(self.standalone_file_path)

    def _trigger_save(self):
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
                self.refresh_workspace_tree()
            else:
                self.update_file_label(norm_saved_path)

    def _refresh_workspace_folder(self):
        if not self.current_workspace_folder:
            return
        self.refresh_workspace_tree()

    def update_file_label(self, path):
        if not self.current_workspace_folder:
            if path and path != "untitled":
                self.workspace_title_lbl.configure(text="STANDALONE FILE", text_color="#4b5263")
                self.standalone_file_path = os.path.normpath(os.path.abspath(path))
                name = os.path.basename(path)
                
                self.standalone_file_btn.configure(text=f"  📄 {name}")
                self.standalone_file_btn.pack(fill="x", padx=5, pady=2, after=self.workspace_title_lbl)
