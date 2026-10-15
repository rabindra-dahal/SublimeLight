"""
SublimeLight - Sidebar Theme Styling Configuration
Sets up the native ttk dark-mode Monokai look and feel for the tree layout.
"""

from tkinter import ttk
import config

class SidebarThemeStyle:
    @staticmethod
    def apply_monokai_theme():
        """Configures the native ttk engine to match the custom editor theme."""
        style = ttk.Style()
        
        # DEFINITIVE ENGINE TRANSLATION PASS:
        # Switching the base layout profile rule engine over to 'alt' or 'default' 
        # completely turns off Windows' native white/gray branch connection line rendering loop!
        style.theme_use("alt")
        
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
        
        # Force tree row borders and gridlines to be non-existent
        style.configure(
            "Sidebar.Treeview", 
            linecolor=config.COLOR_SIDEBAR, 
            indent=14,
            relief="flat"
        )
        
        # Set up modern high-contrast row selection highlights
        style.map(
            "Sidebar.Treeview",
            background=[("selected", "#2c313c"), ("active", "#1e222b")],
            foreground=[("selected", "#a6e22e"), ("active", config.COLOR_TEXT)]
        )
        
        # Strip old window borders from folder headings completely
        style.configure(
            "Sidebar.Treeview.Heading", 
            background=config.COLOR_SIDEBAR, 
            foreground=config.COLOR_TEXT,
            maxbackground=0, 
            borderwidth=0,
            relief="flat"
        )
        return style
