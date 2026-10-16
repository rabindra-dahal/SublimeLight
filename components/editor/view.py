"""
SublimeLight - Core Editor Component View
Provides a smooth, high-performance programming canvas equipped with real-time 
line numbering, stable Monokai syntax highlighting, smart auto-brackets matching, and font size scaling.
"""

import tkinter as tk
import customtkinter as ctk
import re
import os
import config
from .tab_bar import TabBarComponent

class EditorComponent(ctk.CTkFrame):
    def __init__(self, parent, context):
        super().__init__(parent, fg_color=config.COLOR_BG, corner_radius=0)
        self.context = context
        self.context.editor = self
        self.pack_propagate(False)

        self.is_switching_tabs = False
        self.editor_elements_visible = True
        
        # --- ACCESSIBILITY STATE TRACKER ---
        self.current_font_size = 12  # Standard crisp coding default font size baseline

        # 1. Top Tab Strip Bar Controller
        self.tab_bar = TabBarComponent(self, self.context)
        self.tab_bar.pack(side="top", fill="x")

        # 2. Main Editing Layout Workspace Grid Frame
        self.edit_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.edit_frame.pack(side="bottom", fill="both", expand=True)

        # Left Axis: Line Numbers Sidebar Display
        self.line_numbers = tk.Text(
            self.edit_frame, width=4, padx=5, bd=0, 
            bg=config.COLOR_SIDEBAR, fg="#75715E", state="disabled",
            font=("Consolas", self.current_font_size), wrap="none"
        )
        self.line_numbers.pack(side="left", fill="y")

        # Right Axis: Main Interactive Code Typing Surface
        self.text_area = tk.Text(
            self.edit_frame, bg=config.COLOR_BG, fg=config.COLOR_TEXT,
            insertbackground="white", font=("Consolas", self.current_font_size),
            bd=0, padx=10, pady=5, wrap="none", undo=True
        )
        self.text_area.pack(side="right", fill="both", expand=True)

        # --- MONOKAI SYNTAX CONFIGURATION TAGS ---
        self.text_area.tag_config("keyword", foreground="#F92672")  # Pink
        self.text_area.tag_config("builtin", foreground="#66D9EF")  # Cyan
        self.text_area.tag_config("string", foreground="#E6DB74")   # Yellow
        self.text_area.tag_config("comment", foreground="#75715E")  # Grey
        self.text_area.tag_config("number", foreground="#AE81FF")   # Purple

        # 3. REAL-TIME SIGNAL KEY BINDINGS INTERCEPT NETWORKS
        self.text_area.bind("<KeyRelease>", self._on_editor_content_change)
        
        # Smart keyboard auto-brackets intercept handler natively
        self.text_area.bind("<Key>", self._handle_auto_pair_keystrokes)
        
        # Safe Asynchronous Scroll Sync Binding Hooks
        self.text_area.bind("<MouseWheel>", self._synchronize_scroll_viewports)
        self.text_area.bind("<Button-4>", self._synchronize_scroll_viewports)
        self.text_area.bind("<Button-5>", self._synchronize_scroll_viewports)

        # --- ACCESSIBILITY ZOOM SHORTCUT INTERCEPTS ---
        self.text_area.bind("<Control-KeyPress-equal>", lambda event: self._adjust_editor_font_scale(1))   # Ctrl + Plus
        self.text_area.bind("<Control-KeyPress-plus>", lambda event: self._adjust_editor_font_scale(1))    # Numpad Plus
        self.text_area.bind("<Control-KeyPress-minus>", lambda event: self._adjust_editor_font_scale(-1))  # Ctrl - Minus

    def _handle_auto_pair_keystrokes(self, event):
        """Intercepts open bracket and quote entries, auto-injecting closing pairs smoothly."""
        pairs = {
            "(": ")",
            "[": "]",
            "{": "}",
            '"': '"',
            "'": "'"
        }
        
        char = event.char
        if char in pairs:
            self.text_area.insert("insert", char + pairs[char])
            self.text_area.mark_set("insert", "insert-1c")
            self.update_line_count()
            self.highlight_full_document()
            if self.context:
                self.context.save_current_buffer_to_cache()
            return "break"
        return None

    def _adjust_editor_font_scale(self, change_delta):
        """Resizes text fields and updates styles across all tokens dynamically."""
        new_size = self.current_font_size + change_delta
        if 8 <= new_size <= 32:
            self.current_font_size = new_size
            self.text_area.configure(font=("Consolas", self.current_font_size))
            if hasattr(self, 'line_numbers') and self.line_numbers:
                self.line_numbers.configure(font=("Consolas", self.current_font_size))
            self.update_line_count()
            self.highlight_full_document()
        return "break"

    def get_text(self):
        return self.text_area.get("1.0", "end-1c")

    def render_tab_switch_state(self, file_path, text_content):
        self.is_switching_tabs = True
        self.show_editor_elements(True)
        self.text_area.delete("1.0", "end")
        self.text_area.insert("1.0", text_content)
        self.highlight_full_document()
        self.update_line_count()
        self.is_switching_tabs = False
        if hasattr(self.tab_bar, 'rebuild_tab_strip_layout'):
            self.tab_bar.rebuild_tab_strip_layout()

    def update_line_count(self, event=None):
        if self.is_switching_tabs or not self.editor_elements_visible:
            return
        self.line_numbers.configure(state="normal")
        self.line_numbers.delete("1.0", "end")
        
        # Safe integer extraction row selector snippet
        total_lines = int(self.text_area.index("end-1c").split(".")[0])
        
        line_number_string = "\n".join(str(i) for i in range(1, total_lines + 1))
        self.line_numbers.insert("1.0", line_number_string)
        self.line_numbers.configure(state="disabled")
        self._align_line_scrollbar_indices()

    def show_editor_elements(self, visible_flag):
        self.editor_elements_visible = visible_flag
        if visible_flag:
            self.line_numbers.pack(side="left", fill="y")
            self.text_area.pack(side="right", fill="both", expand=True)
        else:
            self.line_numbers.pack_forget()
            self.text_area.pack_forget()

    def highlight_full_document(self):
        """Performs full regex-based Monokai token highlighting across the active document."""
        if not self.editor_elements_visible:
            return

        for tag in ["keyword", "builtin", "string", "comment", "number"]:
            self.text_area.tag_remove(tag, "1.0", "end")

        code_text = self.get_text()

        keywords = r'\b(def|class|return|while|for|in|if|elif|else|break|continue|import|from|as|global|assert|pass|try|except|finally|print)\b'
        builtins = r'\b(str|int|float|list|dict|set|tuple|len|range|enumerate|print|input|open|append|strip|split)\b'
        strings = r'(\".*?\"|\'.*?\')'
        comments = r'(#.*)'
        numbers = r'\b(\d+)\b'

        def apply_regex_tags(pattern, tag_name):
            for match in re.finditer(pattern, code_text):
                start_offset = match.start()
                end_offset = match.end()
                start_idx = self.text_area.index(f"1.0 + {start_offset} chars")
                end_idx = self.text_area.index(f"1.0 + {end_offset} chars")
                self.text_area.tag_add(tag_name, start_idx, end_idx)

        apply_regex_tags(numbers, "number")
        apply_regex_tags(keywords, "keyword")
        apply_regex_tags(builtins, "builtin")
        apply_regex_tags(strings, "string")
        apply_regex_tags(comments, "comment")

    def _on_editor_content_change(self, event):
        if event.keysym not in ("Left", "Right", "Up", "Down", "Control_L", "Control_R", "Shift_L", "Shift_R"):
            self.update_line_count()
            self.highlight_full_document()
            if self.context:
                self.context.save_current_buffer_to_cache()

    def _synchronize_scroll_viewports(self, event):
        self.after(1, self._align_line_scrollbar_indices)

    def _align_line_scrollbar_indices(self):
        try:
            top_fraction, _ = self.text_area.yview()
            self.line_numbers.yview_moveto(top_fraction)
        except:
            pass
