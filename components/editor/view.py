"""
SublimeLight - Editor Component View
Central master framework parsing input actions and orchestrating dynamic tab displays
safely leveraging CustomTkinter's native scroll mechanics without routing locks.
"""

import re
import customtkinter as ctk
import config
from .line_numbers import LineNumbersComponent
from .tab_bar import TabBarComponent

class EditorComponent(ctk.CTkFrame):
    def __init__(self, parent, context):
        super().__init__(parent, fg_color="transparent", corner_radius=0)
        self.context = context
        self.context.editor = self 
        self.editor_elements_visible = False
        self.is_switching_tabs = False

        # 1. Mount Top Closeable Multi-Tab Row Strip Bar
        self.tab_bar = TabBarComponent(self, self.context)
        self.tab_bar.pack(side="top", fill="x")

        # 2. Main Content Container Area
        self.content_area = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.content_area.pack(side="bottom", fill="both", expand=True)

        self.line_numbers = LineNumbersComponent(self.content_area)

        # 3. Code Text Editor Area Box
        # FIXED: Native activate_scrollbars=True handles rendering out of the box cleanly
        self.text_area = ctk.CTkTextbox(
            self.content_area, font=config.FONT_EDITOR, fg_color=config.COLOR_BG,
            text_color=config.COLOR_TEXT, corner_radius=0, border_width=0, activate_scrollbars=True
        )
        self.text_area._textbox.configure(insertbackground=config.COLOR_TEXT)
        self._setup_syntax_tags()
        
        # Bind Event Synchronization Listeners
        self.text_area.bind("<KeyRelease>", self._on_editor_action)
        self.text_area.bind("<ButtonRelease>", self._on_editor_action)
        self.text_area.bind("<Key>", self._on_intercept_keypress) 
        self.text_area.bind("<F5>", self._trigger_code_execution)
        
        self.show_editor_elements(False)

    def show_editor_elements(self, visible=True):
        self.editor_elements_visible = visible
        if visible:
            self.line_numbers.pack(side="left", fill="y", padx=(0, 2))
            self.text_area.pack(side="right", fill="both", expand=True)
            self.update_line_count()
        else:
            self.line_numbers.pack_forget()
            self.text_area.pack_forget()

    def render_tab_switch_state(self, active_path, text_content):
        """Fires from context layer to update active workspace tab configurations securely."""
        if active_path:
            self.is_switching_tabs = True
            self.show_editor_elements(True)
            self.text_area.delete("1.0", "end")
            self.text_area.insert("1.0", text_content)
            self.highlight_full_document()
            self.update_line_count()
            self.is_switching_tabs = False
        else:
            self.show_editor_elements(False)
            
        self.tab_bar.rebuild_tab_strip_layout()

    def set_text(self, text, file_path=None):
        target_path = file_path if file_path else "untitled"
        if self.context:
            self.context.open_new_tab(target_path, text)

    def get_text(self):
        return self.text_area.get("1.0", "end-1c") if self.editor_elements_visible else ""

    def _setup_syntax_tags(self):
        tk_text = self.text_area._textbox
        tk_text.tag_configure("KEYWORD", foreground=config.COLOR_KEYWORD)
        tk_text.tag_configure("STRING", foreground=config.COLOR_STRING)
        tk_text.tag_configure("COMMENT", foreground=config.COLOR_COMMENT)
        tk_text.tag_configure("NUMBER", foreground=config.COLOR_NUMBER)

    def highlight_line(self, line_num):
        if not self.editor_elements_visible:
            return
        tk_text = self.text_area._textbox
        start_idx, end_idx = f"{line_num}.0", f"{line_num}.end"
        for tag in ["KEYWORD", "STRING", "COMMENT", "NUMBER"]:
            tk_text.tag_remove(tag, start_idx, end_idx)
            
        line_text = tk_text.get(start_idx, end_idx)
        for match in re.finditer(r"#.*$", line_text):
            tk_text.tag_add("COMMENT", f"{line_num}.{match.start()}", f"{line_num}.{match.end()}")
            line_text = line_text[:match.start()] + (" " * (match.end() - match.start()))

        string_pattern = r'("(?:[^"\\]|\\.)*")|(\'/d/ML/github-mine/SublimeLight\'(?:[^\'\\]|\\.)*\')'
        for match in re.finditer(string_pattern, line_text):
            tk_text.tag_add("STRING", f"{line_num}.{match.start()}", f"{line_num}.{match.end()}")
            line_text = line_text[:match.start()] + (" " * (match.end() - match.start()))

        for match in re.finditer(r"\b[a-zA-Z_]\w*\b|\b\d+\b", line_text):
            token = match.group()
            token_start, token_end = f"{line_num}.{match.start()}", f"{line_num}.{match.end()}"
            if token in config.PYTHON_KEYWORDS:
                tk_text.tag_add("KEYWORD", token_start, token_end)
            elif token in config.PYTHON_NUMBERS or token.isdigit():
                tk_text.tag_add("NUMBER", token_start, token_end)

    def highlight_full_document(self):
        if not self.editor_elements_visible:
            return
        end_idx = self.text_area.index("end-1c")
        total_lines = int(end_idx.split(".")[0])  
        for line in range(1, total_lines + 1):
            self.highlight_line(line)

    def update_line_count(self):
        if not self.editor_elements_visible:
            return
        end_index = self.text_area.index("end-1c")
        total_lines = int(end_index.split(".")[0])  
        self.line_numbers.redraw(total_lines)

    def _on_intercept_keypress(self, event=None):
        if not self.editor_elements_visible or self.is_switching_tabs:
            return
        current_line = int(self.text_area.index("insert").split(".")[0])  
        self.after(1, lambda: self.highlight_line(current_line))

    def _trigger_code_execution(self, event=None):
        if not self.editor_elements_visible:
            return "break"
        if self.context.sidebar:
            self.context.sidebar._trigger_save()
        if self.context.current_file and self.context.current_file != "untitled":
            import threading
            from services.runner_service import RunnerService
            threading.Thread(target=RunnerService.execute_script, args=(self.context.current_file,), daemon=True).start()
        return "break" 

    def _on_editor_action(self, event=None):
        if not self.editor_elements_visible or self.is_switching_tabs:
            return
            
        if self.context and self.context.current_file:
            self.context.open_tabs[self.context.current_file] = self.get_text()
        self.update_line_count()
        if self.context.statusbar:
            row, col = self.text_area.index("insert").split(".")
            self.context.statusbar.update_coordinates(row, col)
