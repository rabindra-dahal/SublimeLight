"""
SublimeLight - Multi-Tab Bar Component
Dynamically maps multiple tab containers side-by-side with individual close marks.
"""

import os
import customtkinter as ctk
import config

class IndividualTabWidget(ctk.CTkFrame):
    """An individual closeable tab layout element block."""
    def __init__(self, parent, path, on_click, on_close):
        super().__init__(parent, height=30, corner_radius=0)
        self.path = path
        self.pack_propagate(False)
        
        # Shorten filenames dynamically if they extend past bounds
        display_name = os.path.basename(path) if path != "untitled" else "untitled"
        if len(display_name) > 12:
            display_name = display_name[:9] + "..."

        # Interactive File Title Selection Label Button
        # FIXED: Swapped out the distorted snake emoji for a clean document icon
        self.btn_lbl = ctk.CTkButton(
            self, text=f"📄 {display_name}", font=(config.FONT_UI, 11),
            fg_color="transparent", text_color=config.COLOR_TEXT, hover_color="#2c313c",
            anchor="w", width=100, height=30, command=lambda: on_click(self.path)
        )
        self.btn_lbl.pack(side="left", fill="both", expand=True, padx=(5, 0))

        # Individual Close Target Cross
        self.close_btn = ctk.CTkButton(
            self, text="×", font=("Arial", 11, "bold"), width=14, height=14,
            fg_color="transparent", text_color="white",
            hover_color="#e06c75", corner_radius=2, command=lambda: on_close(self.path)
        )
        self.close_btn.pack(side="right", padx=(2, 4), pady=8)


class TabBarComponent(ctk.CTkFrame):
    def __init__(self, parent, context):
        super().__init__(parent, height=35, fg_color=config.COLOR_SIDEBAR, corner_radius=0)
        self.context = context
        self.pack_propagate(False)
        self.rendered_tabs = {} # Tracks instantiated active button objects: {path: widget_instance}

    def rebuild_tab_strip_layout(self):
        """Cleans and systematically redraws all open tab layout structures."""
        # Wipe old widgets from the active view row strip first
        for tab_widget in self.rendered_tabs.values():
            tab_widget.destroy()
        self.rendered_tabs.clear()

        # Reconstruct tabs matching active open tab collections
        for path in self.context.open_tabs.keys():
            # Swap backgrounds to highlight the focused tab cleanly
            is_active = (path == self.context.current_file)
            bg_color = config.COLOR_BG if is_active else config.COLOR_STATUS_BAR
            
            tab_item = IndividualTabWidget(
                self, path, 
                on_click=self.context.set_active_file,
                on_close=self.context.close_tab_session
            )
            tab_item.configure(fg_color=bg_color)
            tab_item.pack(side="left", padx=(2, 0), pady=(5, 0))
            
            self.rendered_tabs[path] = tab_item
