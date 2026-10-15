"""
SublimeLight - File Infrastructure Service
Manages safe file I/O operations and directory scanning utilities.
"""

import os
from tkinter import filedialog, messagebox

class FileService:
    @staticmethod
    def read_file_from_path(file_path):
        """Reads content from a specified absolute file path."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            messagebox.showerror("Disk Error", f"Could not read file stream: {e}")
            return None

    @staticmethod
    def read_file():
        """Opens a file dialog picker and returns the path and content string."""
        file_path = filedialog.askopenfilename(filetypes=[
            ("Python Files", "*.py"), ("Text Files", "*.txt"), ("All Files", "*.*")
        ])
        if not file_path:
            return None, None
        content = FileService.read_file_from_path(file_path)
        return file_path, content

    @staticmethod
    def write_file(file_path, content):
        """Saves current text stream buffer securely back onto local hard drive storage."""
        # FIXED CRITICAL STATE PATH: If the path is missing, None, or explicitly marked "untitled", 
        # force the native Windows dialog picker window to slide open instantly!
        if not file_path or file_path == "untitled":
            file_path = filedialog.asksaveasfilename(
                defaultextension=".py", 
                filetypes=[("Python Files", "*.py"), ("Text Files", "*.txt")]
            )
            
        if not file_path:  # User cancelled the save dialog window
            return None
            
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return file_path
        except Exception as e:
            messagebox.showerror("Disk Error", f"Failed saving current buffer state: {e}")
            return None

    @staticmethod
    def scan_folder():
        """Opens a directory dialog picker and returns a list of files inside it."""
        folder_path = filedialog.askdirectory(mustexist=True)
        if not folder_path:
            return None, []
        
        try:
            all_items = os.listdir(folder_path)
            valid_files = [
                f for f in all_items 
                if os.path.isfile(os.path.join(folder_path, f)) and not f.startswith(".")
            ]
            return folder_path, sorted(valid_files)
        except Exception as e:
            messagebox.showerror("Folder Error", f"Could not scan selected folder: {e}")
            return None, []
