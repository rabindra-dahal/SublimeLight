"""
SublimeLight - Core Entry Point

This file serves as the Application Bootstrapper / Composition Root. 
It instantiates the central state orchestration context, initializes the 
independent frontend components, centers your window matrix, and loads session caches.
"""

import os
import json
import time
import tkinter as tk
import customtkinter as ctk
import config
from core.app_context import AppContext
from components.sidebar.view import SidebarComponent
from components.editor.view import EditorComponent
from components.statusbar.view import StatusbarComponent
from services.runner_service import RunnerService

SESSION_CACHE_FILE = ".sublimelight_session.json"

class SublimeLightApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # 1. Initialize Window Configurations & Apply Screen Centering Math
        self.title("Sublime Light - Python Editor")
        self.configure(fg_color=config.COLOR_BG)
        
        # Center layout window calculation blocks
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (config.WINDOW_WIDTH // 2)
        y = (screen_height // 2) - (config.WINDOW_HEIGHT // 2)
        self.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}+{x}+{y}")

        # 2. Boot Central Orchestrator Domain Context Engine
        self.context = AppContext(self)

        # 3. Native Top Window Menu Strip Assembly
        self._create_top_menu_bar()

        # 4. Construct Layout Panels Frame Containers
        self.workspace_layout = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.workspace_layout.pack(side="top", fill="both", expand=True)

        # 5. Construct and Inject Decoupled Component Interfaces
        self.sidebar = SidebarComponent(self.workspace_layout, self.context)
        self.sidebar.pack(side="left", fill="y")

        self.right_content_pane = ctk.CTkFrame(self.workspace_layout, fg_color="transparent", corner_radius=0)
        self.right_content_pane.pack(side="right", fill="both", expand=True)

        # Stable single-pane text editor layout
        self.editor = EditorComponent(self.right_content_pane, self.context)
        self.editor.pack(side="top", fill="both", expand=True)
        self.context.editor = self.editor

        self.statusbar = StatusbarComponent(self, self.context)
        self.statusbar.pack(side="bottom", fill="x")

        # 6. Global Hotkeys Binding Mapping Lists
        self.bind("<Control-n>", lambda event: self._dispatch_new_file())
        self.bind("<Control-o>", lambda event: self._dispatch_open_file())
        self.bind("<Control-s>", lambda event: self._dispatch_save_file())
        self.bind("<Control-d>", lambda event: self._dispatch_open_folder())
        
        # Core utility keys bindings channels
        self.bind("<KeyPress-F5>", lambda event: self._dispatch_execute_script())
        self.bind("<Control-F5>", lambda event: self._dispatch_launch_native_cmd())

        # 7. Automated Session Cache Loading Hook
        self.after(50, self._load_previous_session)

    def _create_top_menu_bar(self):
        menu_bar = tk.Menu(self)
        
        # --- FILE MENU ---
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New File", accelerator="Ctrl+N", command=self._dispatch_new_file)
        file_menu.add_command(label="Open File...", accelerator="Ctrl+O", command=self._dispatch_open_file)
        file_menu.add_command(label="Open Folder...", accelerator="Ctrl+D", command=self._dispatch_open_folder)
        file_menu.add_separator() 
        file_menu.add_command(label="Save File", accelerator="Ctrl+S", command=self._dispatch_save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # --- RUN MENU ---
        run_menu = tk.Menu(menu_bar, tearoff=0)
        run_menu.add_command(label="Run Python Script", accelerator="F5", command=self._dispatch_execute_script)
        run_menu.add_command(label="Open Command Prompt here...", accelerator="Ctrl+F5", command=self._dispatch_launch_native_cmd)
        menu_bar.add_cascade(label="Run", menu=run_menu)
        
        self.config(menu=menu_bar)

    def _save_session_state(self, folder_path):
        try:
            state_data = {"last_workspace_folder": os.path.normpath(os.path.abspath(folder_path))}
            with open(SESSION_CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(state_data, f, ensure_ascii=False, indent=4)
        except:
            pass

    def _load_previous_session(self):
        if not os.path.exists(SESSION_CACHE_FILE):
            return
        try:
            with open(SESSION_CACHE_FILE, "r", encoding="utf-8") as f:
                state_data = json.load(f)
                previous_folder = state_data.get("last_workspace_folder")
                if previous_folder and os.path.exists(previous_folder) and os.path.isdir(previous_folder):
                    if self.sidebar:
                        self.sidebar.current_workspace_folder = os.path.normpath(previous_folder)
                        folder_name = os.path.basename(self.sidebar.current_workspace_folder).upper()
                        self.sidebar.workspace_title_lbl.configure(text=folder_name, text_color="#5c6370")
                        self.sidebar.refresh_workspace_tree()
        except:
            pass

    def _dispatch_new_file(self):
        if self.context and self.context.sidebar:
            self.context.sidebar._trigger_new_file()

    def _dispatch_open_file(self):
        if self.context and self.context.sidebar:
            self.context.sidebar._trigger_open_file()

    def _dispatch_open_folder(self):
        if self.context and self.context.sidebar:
            self.context.sidebar._trigger_open_folder()
            if self.sidebar and self.sidebar.current_workspace_folder:
                self._save_session_state(self.sidebar.current_workspace_folder)

    def _dispatch_save_file(self):
        if self.context and self.context.sidebar:
            self.context.sidebar._trigger_save()

    def _dispatch_execute_script(self):
        self._dispatch_save_file()
        if self.context and self.context.current_file:
            RunnerService.execute_script(self.context.current_file)

    def _dispatch_launch_native_cmd(self):
        import subprocess
        target_dir = os.getcwd()
        if self.sidebar and self.sidebar.current_workspace_folder:
            target_dir = self.sidebar.current_workspace_folder
        elif self.context and self.context.current_file and os.path.exists(self.context.current_file):
            if os.path.isfile(self.context.current_file):
                target_dir = os.path.dirname(self.context.current_file)
        try:
            subprocess.Popen(["cmd.exe"], creationflags=subprocess.CREATE_NEW_CONSOLE, cwd=target_dir)
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Terminal Error", f"Failed to initialize system console: {e}")

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")  # Force CustomTkinter baseline to stay locked to Dark mode
    app = SublimeLightApp()
    app.mainloop()
