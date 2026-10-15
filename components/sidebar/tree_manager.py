"""
SublimeLight - Sidebar Tree Data Manager
Orchestrates disk discovery actions and manages system node ID key maps.
"""

import os

class SidebarTreeManager:
    def __init__(self, tree_widget):
        self.tree = tree_widget
        self.node_path_map = {}

    def reset_tree(self):
        """Wipes the current node configurations securely."""
        self.tree.delete(*self.tree.get_children())
        self.node_path_map.clear()

    def insert_root_folder(self, folder_path):
        """Mounts the primary workspace folder entry token cleanly on top."""
        self.reset_tree()
        root_name = os.path.basename(folder_path)
        root_node = self.tree.insert("", "end", text=f" 📂  {root_name}", open=True)
        self.node_path_map[root_node] = folder_path
        self.populate_directory_level(root_node, folder_path)

    def populate_directory_level(self, parent_node, target_path):
        """Scans path files, alpha-sorts folders to the top, and appends placeholders lazily."""
        try:
            entries = os.listdir(target_path)
        except PermissionError:
            return

        folders = []
        files = []
        
        for entry in entries:
            if entry.startswith('.'):
                continue
            full_path = os.path.join(target_path, entry)
            if os.path.isdir(full_path):
                folders.append((entry, full_path))
            else:
                files.append((entry, full_path))

        # Sort cleanly by item names to prevent type mismatch crashes
        folders.sort(key=lambda x: x[0].lower())
        files.sort(key=lambda x: x[0].lower())

        # 1. Populate sub-folders with a dummy token for lazy loading expansion
        for name, full_path in folders:
            node = self.tree.insert(parent_node, "end", text=f" 📁  {name}", open=False)
            self.node_path_map[node] = full_path
            self.tree.insert(node, "end", text="DummyToken")

        # 2. Populate standalone file items
        for name, full_path in files:
            node = self.tree.insert(parent_node, "end", text=f" 📄  {name}", open=False)
            self.node_path_map[node] = full_path
