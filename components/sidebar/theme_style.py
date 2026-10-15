"""
SublimeLight - Sidebar Theme Styling Configuration
Sets up the native ttk dark-mode Monokai look and feel for the tree layout.
"""

from tkinter import ttk
import customtkinter as ctk
import config

class SidebarThemeStyle:
    @staticmethod
    def apply_monokai_theme():
        """Configures the native ttk engine to match the custom editor theme."""
        style = ttk.Style()
        style.theme_use("clam")
        
        # Structure the modern dark sidebar rows
        style.configure(
            "Sidebar.Treeview",
            background=config.COLOR_SIDEBAR,
            fieldbackground=config.COLOR_SIDEBAR,
            foreground=config.COLOR_TEXT,
            rowheight=24,
            bd=0,
            borderwidth=0,
            highlightthickness=0,
            font=(config.FONT_UI, 11)
        )
        
        # Set up modern high-contrast row selection highlights
        style.map(
            "Sidebar.Treeview",
            background=[("selected", "#2c313c"), ("active", "#1e222b")],
            foreground=[("selected", "#a6e22e"), ("active", config.COLOR_TEXT)]
        )
        
        # Strip old window borders from folder headings
        style.configure(
            "Sidebar.Treeview.Heading", 
            background=config.COLOR_SIDEBAR, 
            maxbackground=0, 
            borderwidth=0,
            relief="flat"
        )
        return style
