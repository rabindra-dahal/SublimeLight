"""
SublimeLight - Line Numbers Component
A narrow, read-only textbox column that displays document line counts.
"""

import customtkinter as ctk
import config

class LineNumbersComponent(ctk.CTkTextbox):
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent, 
            width=45, 
            font=config.FONT_EDITOR, 
            fg_color=config.COLOR_SIDEBAR, 
            text_color="#5c6370",          
            corner_radius=0,
            border_width=0,
            activate_scrollbars=False      
        )
        self.configure(state="disabled")
        self._textbox.configure(cursor="arrow", selectbackground=config.COLOR_SIDEBAR)

    def redraw(self, total_lines):
        """Refreshes the numeric list track display stream cleanly."""
        self.configure(state="normal")
        self.delete("1.0", "end")
        numbers_string = "\n".join(str(i) for i in range(1, total_lines + 1))
        self.insert("1.0", numbers_string)
        self.configure(state="disabled")
