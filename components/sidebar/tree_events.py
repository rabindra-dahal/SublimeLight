"""
SublimeLight - Sidebar Tree Event Controller
Captures UI actions, coordinates icon switches, and handles document openings.
"""

import os
from services.file_service import FileService

class SidebarTreeEvents:
    def __init__(self, tree_widget, data_manager, context):
        self.tree = tree_widget
        self.manager = data_manager
        self.context = context

    def handle_folder_expand(self, event):
        """Toggles folder icons to 'Open 📂' and processes dynamic lazy-loading tasks."""
        selected_nodes = self.tree.selection()
        if not selected_nodes:
            return
        selected_item = selected_nodes[0]
        
        current_text = self.tree.item(selected_item, "text")
        if "📁" in current_text:
            self.tree.item(selected_item, text=current_text.replace("📁", "📂"))

        children = self.tree.get_children(selected_item)
        if len(children) == 1 and self.tree.item(children[0], "text") == "DummyToken":
            self.tree.delete(children[0])
            real_path = self.manager.node_path_map.get(selected_item)
            if real_path:
                self.manager.populate_directory_level(selected_item, real_path)

    def handle_folder_collapse(self, event):
        """Toggles folder icons cleanly back to 'Closed 📁' upon closure."""
        selected_nodes = self.tree.selection()
        if not selected_nodes:
            return
        selected_item = selected_nodes[0]
        
        current_text = self.tree.item(selected_item, "text")
        if "📂" in current_text:
            self.tree.item(selected_item, text=current_text.replace("📂", "📁"))

    def handle_item_double_click(self, event):
        """Loads selected file contents directly into the main text editor views."""
        selected_items = self.tree.selection()
        if not selected_items:
            return
            
        selected_item = selected_items[0]
        real_path = self.manager.node_path_map.get(selected_item)
        
        if real_path and os.path.isfile(real_path):
            norm_path = os.path.normpath(os.path.abspath(real_path))
            text = FileService.read_file_from_path(norm_path)
            if text is not None:
                self.context.open_new_tab(norm_path, text)

    def handle_single_click_select(self, event):
        """Forces highlighted row selection changes on mouse focus tracks immediately."""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
