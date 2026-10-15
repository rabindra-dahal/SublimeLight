"""
SublimeLight - Sidebar Component View
Handles nested directory operations, sub-folder tree exploration grids,
and project workspaces fully integrated with focus-activated global scroll triggers.
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

        # FIXED FOCUS-ACTIVATED SCROLL: Bind to entry/exit triggers on the root frame 
        # to isolate global mouse wheel capture safely without touching the editor on the right!
        self.bind("<Enter>", self._activate_sidebar_scroll)
        self.bind("<Leave>", self._deactivate_sidebar_scroll)

    def _activate_sidebar_scroll(self, event=None):
        """Locks the global window scroll wheel track to move this sidebar panel frame when hovered."""
        self.bind_all("<MouseWheel>", self._on_sidebar_scroll)

    def _deactivate_sidebar_scroll(self, event=None):
        """Instantly unbinds the scroll wheel listener the millisecond your cursor exits the sidebar boundaries."""
        self.unbind_all("<MouseWheel>")

    def _on_sidebar_scroll(self, event):
        """Passes mouse wheel spin signals straight to the sidebar's parent canvas engine."""
        if hasattr(self.files_scroll_frame, "_canvas") and self.files_scroll_frame._canvas:
            try:
                self.files_scroll_frame._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except:
                pass

    def _trigger_new_file(self):
        """Clears file state contexts to initialize a blank document track inside a tab."""
        self.standalone_file_btn.pack_forget()
        self.standalone_file_path = None
        self.context.open_new_tab("untitled", "")

    def _trigger_open_file(self):
        """Loads a standalone individual file selection directly into a new tab container."""
        path, text = FileService.read_file()
        if path is not None:
            self.current_workspace_folder = None
            self._clear_tree_widgets()
            
            norm_path = os.path.normpath(os.path.abspath(path))
            self.context.open_new_tab(norm_path, text)

    def _trigger_open_folder(self):
        """Scans a selected folder directory and populates file lists onto the sidebar view panel."""
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
        """Wipes old visual widgets out of the sidebar tree block safely."""
        for widget in self.active_tree_widgets:
            widget.destroy()
        self.active_tree_widgets.clear()

    def refresh_workspace_tree(self):
        """Triggers a clean pass of your folder structures and updates scroll parameters."""
        if not self.current_workspace_folder:
            return
        self._clear_tree_widgets()
        self._render_directory_level(self.current_workspace_folder, indent_level=0)
        self.files_scroll_frame.update_idletasks()

    def _render_directory_level(self, target_dir, indent_level):
        """Recursive layout renderer sorting sub-folders to the top and indenting child files cleanly."""
        try:
            items = os.listdir(target_dir)
        except:
            return

        folders = []
        files = []
        
        for item in items:
            if item.startswith('.'): 
                continue
            full_path = os.path.join(target_dir, item)
            if os.path.isdir(full_path):
                folders.append((item, full_path))
            else:
                files.append((item, full_path))

        folders.sort(key=lambda x: x.lower())
        files.sort(key=lambda x: x.lower())

        # 1. DRAW SUB-FOLDERS
        for name, full_path in folders:
            is_expanded = full_path in self.expanded_folders
            icon = "▼ 📂" if is_expanded else "▶ 📁"
            padding_left = 5 + (indent_level * 12) 
            
            folder_btn = ctk.CTkButton(
                self.files_scroll_frame,
                text=f"{icon} {name}",
                font=(config.FONT_UI, 12, "bold"),
                fg_color="transparent",
                text_color="#a6e22e", 
                hover_color="#2c313c",
                anchor="w",
                height=22,
                command=lambda p=full_path: self._toggle_folder_state(p)
            )
            folder_btn.pack(fill="x", padx=(padding_left, 5), pady=1)
            
            # FIXED SCROLL LINKING: Let parent entry focus handlers capture mouse gestures globally inside this frame
            folder_btn.bind("<Enter>", self._activate_sidebar_scroll)
            
            self.active_tree_widgets.append(folder_btn)

            if is_expanded:
                self._render_directory_level(full_path, indent_level + 1)

        # 2. DRAW CHILD FILES
        for name, full_path in files:
            padding_left = 18 + (indent_level * 12) 
            
            file_btn = ctk.CTkButton(
                self.files_scroll_frame,
                text=f"📄 {name}",
                font=(config.FONT_UI, 11),
                fg_color="transparent",
                text_color=config.COLOR_TEXT,
                hover_color="#2c313c",
                anchor="w",
                height=22,
                command=lambda p=full_path: self._load_file_from_sidebar(p)
            )
            file_btn.pack(fill="x", padx=(padding_left, 5), pady=1)
            
            # FIXED SCROLL LINKING: Let parent entry focus handlers capture mouse gestures globally inside this frame
            file_btn.bind("<Enter>", self._activate_sidebar_scroll)
            
            self.active_tree_widgets.append(file_btn)

    def _toggle_folder_state(self, folder_path):
        """Swaps sub-folder states in memory and immediately triggers a sidebar redrawing pass."""
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
