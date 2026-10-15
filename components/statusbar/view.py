"""
SublimeLight - Statusbar Component View
Renders tracking logs, row/column indicators, and syntax types dynamically.
"""

import customtkinter as ctk
import config

class StatusbarComponent(ctk.CTkFrame):
    def __init__(self, parent, context):
        super().__init__(parent, height=25, fg_color=config.COLOR_STATUS_BAR, corner_radius=0)
        self.context = context
        self.context.statusbar = self  # Register this component self-reference with the context brain
        self.pack_propagate(False)
        
        # --- Footnote Indicator Layouts Assembly ---
        self.pos_lbl = ctk.CTkLabel(
            self, text="Line 1, Column 0", 
            font=(config.FONT_EDITOR[0], 11), text_color="#9da5b4"
        )
        self.pos_lbl.pack(side="left", padx=15)
        
        self.lang_lbl = ctk.CTkLabel(
            self, text="Plain Text", 
            font=(config.FONT_EDITOR[0], 11), text_color="#9da5b4"
        )
        self.lang_lbl.pack(side="right", padx=15)

    def update_coordinates(self, row, col):
        """Modifies row/column UI indicator metrics labels dynamically."""
        self.pos_lbl.configure(text=f"Line {row}, Column {col}")

    def update_language(self, path):
        """Determines programming syntax tags dynamically based on the file extension."""
        if not path:
            text = "Plain Text"
        elif path.endswith(".py"):
            text = "Python"
        elif path.endswith((".cc", ".cpp", ".h")):
            text = "C++"
        else:
            text = "Plain Text"
        self.lang_lbl.configure(text=text)
