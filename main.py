"""
SublimeLight - Core Entry Point

This file serves as the Application Bootstrapper / Composition Root. 
It instantiates the central state orchestration context, initializes the 
independent frontend components, and maps your stable single-pane text editor layout.
"""

import time
import tkinter as tk
import customtkinter as ctk
import config
from core.app_context import AppContext
from components.sidebar.view import SidebarComponent
from components.editor.view import EditorComponent
from components.statusbar.view import StatusbarComponent

class SublimeLightApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # 1. Initialize Window Configurations
        self.title("Sublime Light - Python Editor")
        self.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.configure(fg_color=config.COLOR_BG)

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

        # RESTORED STABLE SINGLE-PANE VIEW: Put EditorComponent directly back into the layout
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

    def _create_top_menu_bar(self):
        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New File", accelerator="Ctrl+N", command=self._dispatch_new_file)
        file_menu.add_command(label="Open File...", accelerator="Ctrl+O", command=self._dispatch_open_file)
        file_menu.add_command(label="Open Folder...", accelerator="Ctrl+D", command=self._dispatch_open_folder)
        file_menu.add_separator() 
        file_menu.add_command(label="Save File", accelerator="Ctrl+S", command=self._dispatch_save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Undo", accelerator="Ctrl+Z")
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        
        menu_bar.add_cascade(label="Selection", menu=tk.Menu(menu_bar, tearoff=0))
        menu_bar.add_cascade(label="View", menu=tk.Menu(menu_bar, tearoff=0))
        self.config(menu=menu_bar)

    def _dispatch_new_file(self):
        if self.context and self.context.sidebar:
            self.context.sidebar._trigger_new_file()

    def _dispatch_open_file(self):
        if self.context and self.context.sidebar:
            self.context.sidebar._trigger_open_file()

    def _dispatch_open_folder(self):
        if self.context and self.context.sidebar:
            self.context.sidebar._trigger_open_folder()

    def _dispatch_save_file(self):
        if self.context and self.context.sidebar:
            self.context.sidebar._trigger_save()

if __name__ == "__main__":
    app = SublimeLightApp()
    app.mainloop()
