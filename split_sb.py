"""
SublimeLight Layout Sandbox - Automated Vertical Window Split
Demonstrates a responsive, side-by-side dual editor layout panel matrix.
"""

import tkinter as tk
from tkinter import ttk

class SplitLayoutSandbox(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SublimeLight Pane Matrix Split View")
        self.geometry("900x500")
        self.configure(bg="#1e1e1e")

        # Style configuration pass to match our Monokai IDE aesthetic
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Style the middle slider sash to be a minimal dark separator bar
        self.style.configure(
            "PanedWindow", 
            background="#1e1e1e", 
            sashrelief="flat", 
            sashwidth=4
        )

        # 1. Instantiate a Native Native PanedWindow (Split Container)
        # This handles dynamic horizontal scaling and routes resize drags naturally
        self.split_pane_container = tk.PanedWindow(
            self, orient=tk.HORIZONTAL, bd=0, bg="#1a1a1a", sashwidth=4, relief="flat"
        )
        self.split_pane_container.pack(fill="both", expand=True, padx=5, pady=5)

        # 2. Left Editor Workspace Pane
        self.left_editor_frame = tk.Frame(self.split_pane_container, bg="#1e1e1e")
        left_lbl = tk.Label(
            self.left_editor_frame, text="PANE A: hello.py", 
            font=("Arial", 10, "bold"), fg="#75715E", bg="#1e1e1e", anchor="w"
        )
        left_lbl.pack(fill="x", padx=10, pady=5)
        
        self.left_text = tk.Text(
            self.left_editor_frame, bg="#272822", fg="#F8F8F2", 
            insertbackground="white", font=("Consolas", 11), bd=0, padx=10
        )
        self.left_text.insert("1.0", "def main():\n    print('Hello from Left Pane!')\n")
        self.left_text.pack(fill="both", expand=True)

        # 3. Right Editor Workspace Pane
        self.right_editor_frame = tk.Frame(self.split_pane_container, bg="#1e1e1e")
        right_lbl = tk.Label(
            self.right_editor_frame, text="PANE B: hi.py", 
            font=("Arial", 10, "bold"), fg="#75715E", bg="#1e1e1e", anchor="w"
        )
        right_lbl.pack(fill="x", padx=10, pady=5)
        
        self.right_text = tk.Text(
            self.right_editor_frame, bg="#272822", fg="#F8F8F2", 
            insertbackground="white", font=("Consolas", 11), bd=0, padx=10
        )
        self.right_text.insert("1.0", "def greet():\n    print('Hello from Right Pane!')\n")
        self.right_text.pack(fill="both", expand=True)

        # 4. Mount the panes into the master layout split paned controller
        self.split_pane_container.add(self.left_editor_frame, stretch="always", minsize=200)
        self.split_pane_container.add(self.right_editor_frame, stretch="always", minsize=200)

if __name__ == "__main__":
    app = SplitLayoutSandbox()
    app.mainloop()
