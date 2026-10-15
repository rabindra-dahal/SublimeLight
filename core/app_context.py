"""Central application state broker routing multiple tab operations cleanly without interfering with terminals."""

import os

class AppContext:
    def __init__(self, root_window):
        self.root = root_window
        self.current_file = None  # Holds the absolute path string or "untitled"
        self.open_tabs = {}       # Maps {normalized_abs_path_string: content_string}
        
        # Component References Registry
        self.sidebar = None
        self.editor = None
        self.statusbar = None
        self.terminal = None  

    def open_new_tab(self, file_path, content_text):
        """Registers a newly opened file inside our tab dictionary or focuses it if already open."""
        if file_path and file_path != "untitled":
            abs_path = os.path.normpath(os.path.abspath(file_path))
        else:
            abs_path = "untitled"
            
        # Cache current active textbox state string before switching views
        if self.current_file and self.editor:
            self.open_tabs[self.current_file] = self.editor.get_text()
            
        if abs_path not in self.open_tabs:
            self.open_tabs[abs_path] = content_text
            
        self.set_active_file(abs_path)

    def save_current_buffer_to_cache(self):
        """Saves current visible text editor contents straight into volatile tab memory arrays."""
        if self.current_file and self.editor:
            self.open_tabs[self.current_file] = self.editor.get_text()

    def set_active_file(self, file_path):
        """State machine modifier updating workspace tracking logs safely without moving the terminal."""
        if not file_path:
            self.current_file = None
            if self.editor:
                self.editor.show_editor_elements(False)
            return

        if file_path == "untitled":
            self.current_file = "untitled"
        else:
            self.current_file = os.path.normpath(os.path.abspath(file_path))
            
            # FIXED: Automatic terminal synchronization code block is completely deleted.
            # Shifting focus across different tabs or sidebar clicks will never alter the shell path.
        
        text_content = self.open_tabs.get(self.current_file, "")

        if self.statusbar:
            self.statusbar.update_language(self.current_file)
        if self.sidebar:
            self.sidebar.update_file_label(self.current_file)
        if self.editor:
            self.editor.render_tab_switch_state(self.current_file, text_content)
            
    def close_tab_session(self, file_path):
        """Removes a tab from the active registry memory and switches focus to remaining tabs."""
        normalized_path = os.path.normpath(os.path.abspath(file_path)) if file_path and file_path != "untitled" else file_path
        if normalized_path in self.open_tabs:
            del self.open_tabs[normalized_path]
            
        if self.open_tabs:
            remaining_keys = list(self.open_tabs.keys())
            self.open_new_tab(remaining_keys[-1], self.open_tabs[remaining_keys[-1]])
        else:
            self.current_file = None
            if self.editor:
                self.editor.text_area.delete("1.0", "end")
                self.editor.show_editor_elements(False)
                self.editor.tab_bar.rebuild_tab_strip_layout()
