"""
SublimeLight - Core Editor Component View
Provides a clean, modular programming canvas backed by decoupled search panels,
independent regex token syntax highlight engines, and smart layout formatting.
"""

import tkinter as tk
import customtkinter as ctk
import re
import config

from .tab_bar import TabBarComponent
from .search_panel import SearchPanelComponent
from .highlighter import SyntaxHighlighter

class EditorComponent(ctk.CTkFrame):
    def __init__(self, parent, context):
        super().__init__(parent, fg_color=config.COLOR_BG, corner_radius=0)
        self.context = context
        self.context.editor = self
        self.pack_propagate(False)

        self.is_switching_tabs = False
        self.editor_elements_visible = True
        self.is_find_panel_visible = False
        self.current_font_size = 12

        # --- GRID CONTROLS ---
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Mount layouts row-by-row
        self.tab_bar = TabBarComponent(self, self.context)
        self.tab_bar.grid(row=0, column=0, sticky="ew")

        self.edit_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.edit_frame.grid(row=1, column=0, sticky="nsew")

        self.line_numbers = tk.Text(
            self.edit_frame, width=4, padx=5, bd=0, bg=config.COLOR_SIDEBAR, 
            fg="#75715E", state="disabled", font=("Consolas", self.current_font_size), wrap="none"
        )
        self.line_numbers.pack(side="left", fill="y")

        self.text_area = tk.Text(
            self.edit_frame, bg=config.COLOR_BG, fg=config.COLOR_TEXT, insertbackground="white", 
            font=("Consolas", self.current_font_size), bd=0, padx=10, pady=5, wrap="none", undo=True
        )
        self.text_area.pack(side="right", fill="both", expand=True)

        # --- EXTENSION INITIALIZATIONS ---
        self.highlighter = SyntaxHighlighter(self.text_area)
        self.find_panel = SearchPanelComponent(
            self, self.text_area, self.update_line_count, 
            self.highlighter.highlight, self.context
        )

        # --- EVENT INTERCEPTS BINDINGS ---
        self.text_area.bind("<KeyRelease>", self._on_editor_content_change)
        self.text_area.bind("<Key>", self._handle_auto_pair_keystrokes)
        self.text_area.bind("<Return>", self._handle_smart_auto_indentation)
        
        self.text_area.bind("<MouseWheel>", self._synchronize_scroll_viewports)
        self.text_area.bind("<Button-4>", self._synchronize_scroll_viewports)
        self.text_area.bind("<Button-5>", self._synchronize_scroll_viewports)

        self.text_area.bind("<Control-KeyPress-equal>", lambda e: self._adjust_editor_font_scale(1))
        self.text_area.bind("<Control-KeyPress-plus>", lambda e: self._adjust_editor_font_scale(1))
        self.text_area.bind("<Control-KeyPress-minus>", lambda e: self._adjust_editor_font_scale(-1))
        self.text_area.bind("<Control-f>", lambda e: self.toggle_find_panel())

    def _handle_smart_auto_indentation(self, event):
        try:
            current_index = self.text_area.index("insert")
            row, col = map(int, current_index.split("."))
            line_content = self.text_area.get(f"{row}.0", current_index)

            whitespace_match = re.match(r'^([ \t]*)', line_content)
            leading_whitespace = whitespace_match.group(1) if whitespace_match else ""

            extra_indent = "    " if line_content.strip().endswith(":") else ""
            self.text_area.insert("insert", "\n" + leading_whitespace + extra_indent)

            self.update_line_count()
            self.highlighter.highlight(self.editor_elements_visible)
            
            if self.is_find_panel_visible:
                self.find_panel.execute_live_text_search()
            if self.context:
                self.context.save_current_buffer_to_cache()
            return "break"
        except:
            return None

    def toggle_find_panel(self):
        if not self.is_find_panel_visible:
            self.find_panel.grid(row=2, column=0, sticky="ew")
            self.find_panel.find_entry.focus_set()
            self.is_find_panel_visible = True
            self.find_panel.execute_live_text_search()
        else:
            self.text_area.tag_remove("search_match", "1.0", "end")
            self.find_panel.grid_forget()
            self.text_area.focus_set()
            self.is_find_panel_visible = False
        return "break"

    def get_text(self):
        return self.text_area.get("1.0", "end-1c")

    def render_tab_switch_state(self, file_path, text_content):
        self.is_switching_tabs = True
        self.show_editor_elements(True)
        self.text_area.delete("1.0", "end")
        self.text_area.insert("1.0", text_content)
        
        if self.is_find_panel_visible:
            self.find_panel.execute_live_text_search()
        else:
            self.text_area.tag_remove("search_match", "1.0", "end")
            
        self.highlighter.highlight(self.editor_elements_visible)
        self.update_line_count()
        self.is_switching_tabs = False
        if hasattr(self.tab_bar, 'rebuild_tab_strip_layout'):
            self.tab_bar.rebuild_tab_strip_layout()

    def update_line_count(self, event=None):
        if self.is_switching_tabs or not self.editor_elements_visible:
            return
        self.line_numbers.configure(state="normal")
        self.line_numbers.delete("1.0", "end")
        
        total_lines = int(self.text_area.index("end-1c").split(".")[0])
        line_number_string = "\n".join(str(i) for i in range(1, total_lines + 1))
        
        self.line_numbers.insert("1.0", line_number_string)
        self.line_numbers.configure(state="disabled")
        self._align_line_scrollbar_indices()

    def show_editor_elements(self, visible_flag):
        self.editor_elements_visible = visible_flag
        if visible_flag:
            self.edit_frame.grid(row=1, column=0, sticky="nsew")
        else:
            self.edit_frame.grid_forget()
            self.find_panel.grid_forget()
            self.is_find_panel_visible = False

    def _handle_auto_pair_keystrokes(self, event):
        pairs = {"(": ")", "[": "]", "{": "}", '"': '"', "'": "'"}
        char = event.char
        if char in pairs:
            self.text_area.insert("insert", char + pairs[char])
            self.text_area.mark_set("insert", "insert-1c")
            self.update_line_count()
            self.highlighter.highlight(self.editor_elements_visible)
            if self.is_find_panel_visible:
                self.find_panel.execute_live_text_search()
            if self.context:
                self.context.save_current_buffer_to_cache()
            return "break"
        return None

    def _adjust_editor_font_scale(self, change_delta):
        new_size = self.current_font_size + change_delta
        if 8 <= new_size <= 32:
            self.current_font_size = new_size
            self.text_area.configure(font=("Consolas", self.current_font_size))
            if hasattr(self, 'line_numbers') and self.line_numbers:
                self.line_numbers.configure(font=("Consolas", self.current_font_size))
            self.update_line_count()
            self.highlighter.highlight(self.editor_elements_visible)
        return "break"

    def _on_editor_content_change(self, event):
        if event.keysym not in ("Left", "Right", "Up", "Down", "Control_L", "Control_R", "Shift_L", "Shift_R", "Return"):
            self.update_line_count()
            self.highlighter.highlight(self.editor_elements_visible)
            if self.is_find_panel_visible:
                self.find_panel.execute_live_text_search()
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
