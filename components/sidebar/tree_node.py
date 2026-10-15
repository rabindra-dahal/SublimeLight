"""
SublimeLight - Sidebar Tree Node
Dedicated component rendering individual file or directory items with robust scroll forwarding.
Supports full multi-device scrolling for both hardware mouse wheels and laptop touchpads.
"""

import os
import customtkinter as ctk
import config

class TreeNodeButton(ctk.CTkButton):
    def __init__(self, master, name, full_path, is_folder, is_expanded, indent_level, toggle_cmd, load_cmd, scroll_frame):
        padding_left = 5 + (indent_level * 12) if is_folder else 18 + (indent_level * 12)
        text_color = "#a6e22e" if is_folder else config.COLOR_TEXT
        font_weight = "bold" if is_folder else "normal"
        icon = ("▼ 📂 " if is_expanded else "▶ 📁 ") if is_folder else "📄 "
        
        action_cmd = (lambda: toggle_cmd(full_path)) if is_folder else (lambda: load_cmd(full_path))

        super().__init__(
            master,
            text=f"{icon}{name}",
            font=(config.FONT_UI, 11 if not is_folder else 12, font_weight),
            fg_color="transparent",
            text_color=text_color,
            hover_color="#2c313c",
            anchor="w",
            height=22,
            command=action_cmd
        )
        self.scroll_frame = scroll_frame
        self.pack(fill="x", padx=(padding_left, 5), pady=1)
        
        # --- UNIVERSAL TRACKPAD & MOUSE WHEEL INTERCEPT TRACKS ---
        # 1. Bind events onto the base button skin layer
        self.bind("<MouseWheel>", self._forward_mouse_wheel)
        
        # 2. Wait 10ms for layout processing, then map sub-element drawing layers
        self.after(10, self._bind_internal_sub_elements)

    def _bind_internal_sub_elements(self):
        """Binds dual-input scroll handlers directly to hidden internal text labels and canvas boxes."""
        for layer in ["_text_label", "_canvas"]:
            if hasattr(self, layer) and getattr(self, layer):
                target_node = getattr(self, layer)
                target_node.bind("<MouseWheel>", self._forward_mouse_wheel)

    def _forward_mouse_wheel(self, event):
        """Universal scroll engine normalizing physical wheel clicks and high-precision laptop swipes."""
        if hasattr(self.scroll_frame, "_canvas") and self.scroll_frame._canvas:
            try:
                # Force canvas to check its size boundaries
                self.scroll_frame._canvas.configure(scrollregion=self.scroll_frame._canvas.bbox("all"))
                
                # TOUCHPAD NORMALIZATION ROUTINE:
                # Windows hardware wheels return macro increments of 120. 
                # Laptop trackpads return fluid, variable micro-deltas or fraction units under 120.
                if abs(event.delta) >= 120:
                    scroll_units = int(-1 * (event.delta / 120))
                else:
                    # Catch high-precision trackpad micro-steps smoothly based on direction
                    scroll_units = -1 if event.delta > 0 else 1
                
                # Direct-drive the native Tkinter yview container
                if scroll_units != 0:
                    self.scroll_frame._canvas.yview_scroll(scroll_units, "units")
            except:
                pass
