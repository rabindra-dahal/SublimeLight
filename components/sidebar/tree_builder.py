"""
SublimeLight - Sidebar Tree Builder
Engine class parsing local directory listings and compiling sorted data collections.
"""

import os

class TreeBuilder:
    @staticmethod
    def scan_and_sort_directory(target_dir):
        """Scans path coordinates on the drive and splits items into alpha-sorted name/path tuples."""
        try:
            items = os.listdir(target_dir)
        except:
            return [], []

        folders = []
        files = []
        
        for item in items:
            if item.startswith('.'): # Skip internal metadata links or hidden system files
                continue
            full_path = os.path.join(target_dir, item)
            if os.path.isdir(full_path):
                folders.append((item, full_path))
            else:
                files.append((item, full_path))

        # FIXED TUPLE SORTING: Look explicitly at slot index 0 to sort cleanly by string names!
        folders.sort(key=lambda x: x[0].lower())
        files.sort(key=lambda x: x[0].lower())
        
        return folders, files
