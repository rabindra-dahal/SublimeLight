"""
SublimeLight - Integrated Terminal Component View
Provides a toggleable command prompt panel shell inside a CustomTkinter textbox frame.
"""

import os
import sys
import subprocess
import threading
import customtkinter as ctk
import config

class TerminalComponent(ctk.CTkFrame):
    def __init__(self, parent, context):
        super().__init__(parent, height=220, fg_color="#111111", corner_radius=0)
        self.context = context
        self.pack_propagate(False)

        # 1. Terminal Panel Header Accent Title
        self.header_frame = ctk.CTkFrame(self, height=25, fg_color="#1a1a1a", corner_radius=0)
        self.header_frame.pack(side="top", fill="x")
        self.header_frame.pack_propagate(False)

        self.title_lbl = ctk.CTkLabel(
            self.header_frame, text="TERMINAL (bash/cmd proxy)", 
            font=("Arial", 10, "bold"), text_color="#75715E"
        )
        self.title_lbl.pack(side="left", padx=15)

        # 2. Command Display/Input Area Text Container
        self.text_area = ctk.CTkTextbox(
            self, font=("Consolas", 12), fg_color="#111111", 
            text_color="#A9FFB2", border_width=0, corner_radius=0
        )
        self.text_area.pack(side="bottom", fill="both", expand=True)

        # 3. Initialize Terminal System Directories & DYNAMIC PROMPT
        self.current_dir = os.path.normpath(os.getcwd())
        
        # Run dynamic check right on startup instead of hardcoding (venv)
        self.prompt_string = self._generate_dynamic_prompt()
        
        # Draw Welcome Message block
        self.text_area.insert("end", "=== SUBLIMELIGHT INTEGRATED TERMINAL SHELL ===\nType commands natively. Press Ctrl+Shift to toggle visibility.\n")
        self._print_prompt()

        # Intercept Return keystrokes to process custom commands parsing
        self.text_area.bind("<Return>", self._on_enter_command)
        
        # Freeze backspace parameters to stop users from deleting the directory prompt strings
        self.text_area.bind("<Key>", self._restrict_cursor_bounds)

    def _generate_dynamic_prompt(self):
        """DYNAMIC CHECK: Only displays a virtual environment tag if a real venv folder exists inside the active workspace."""
        # Define standard virtual environment activation directories for Windows and Linux
        windows_venv_check = os.path.join(self.current_dir, "Scripts", "activate.bat")
        linux_venv_check = os.path.join(self.current_dir, "bin", "activate")
        
        # Look for typical virtual environment folders inside the current workspace (like 'venv' or '.venv')
        has_local_venv = os.path.exists(windows_venv_check) or os.path.exists(linux_venv_check)
        
        if has_local_venv:
            # If the user explicitly built a virtual environment inside their project folder, display it
            return f"\n(venv) {self.current_dir}\n$ "
        else:
            # Clean prompt line with zero hardcoded virtual labels for normal desktop folders
            return f"\n{self.current_dir}\n$ "


    def _print_prompt(self):
        """Appends the current system working directory line string."""
        self.text_area.insert("end", self.prompt_string)
        self.text_area.see("end")
        self.text_area.mark_set("insert", "end")
        self.command_start_index = self.text_area.index("insert")

    def _on_enter_command(self, event):
        """Extracts the written text parameters on line entries and dispatches execution tasks."""
        command_raw = self.text_area.get(self.command_start_index, "end-1c").strip()
        
        if not command_raw:
            self.after(1, self._print_prompt)
            return "break"

        # Intercept clear/cls commands natively before they reach Windows
        if command_raw.lower() in ("clear", "cls"):
            self.text_area.delete("1.0", "end")
            self.after(1, self._print_prompt)
            return "break"

        # Intercept directory adjustments 'cd' natively inside our Python wrapper engine
        if command_raw.startswith("cd "):
            target_dir = command_raw[3:].strip().strip('"').strip("'")
            if target_dir == "..":
                self.current_dir = os.path.normpath(os.path.dirname(self.current_dir))
                os.chdir(self.current_dir)
            elif os.path.exists(target_dir):
                self.current_dir = os.path.normpath(os.path.abspath(target_dir))
                os.chdir(self.current_dir)
            else:
                self.text_area.insert("end", f"\nSystem cannot find the specified directory path: {target_dir}")
            
            # FIXED: Call our dynamic environment checker method here instead of hardcoding (venv)!
            self.prompt_string = self._generate_dynamic_prompt()
            self.after(1, self._print_prompt)
            return "break"

        # Execute system applications asynchronously in background workers
        self.text_area.insert("end", "\n")
        threading.Thread(target=self._async_run_process, args=(command_raw,), daemon=True).start()
        return "break" 

    def _async_run_process(self, command_str):
        """Runs native system executables cleanly inside detached execution threads."""
        try:
            process = subprocess.Popen(
                command_str, shell=True, cwd=self.current_dir,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            stdout, stderr = process.communicate()
            
            if stdout:
                self.text_area.insert("end", stdout)
            if stderr:
                self.text_area.insert("end", stderr)
        except Exception as e:
            self.text_area.insert("end", f"Execution Engine Failure: {e}\n")
            
        self.after(1, self._print_prompt)

    def _restrict_cursor_bounds(self, event):
        """Keeps the typing insertion point locked safely ahead of prompt boundary metrics."""
        if event.keysym in ("BackSpace", "Left"):
            current_insert = self.text_area.index("insert")
            if self.text_area.compare(current_insert, "<=", self.command_start_index):
                return "break" 

    def sync_workspace_directory(self, folder_path):
        """Dynamic hook that instantly forces the shell to change its directory focus."""
        if not folder_path or not os.path.exists(folder_path):
            return
            
        try:
            self.current_dir = os.path.normpath(os.path.abspath(folder_path))
            os.chdir(self.current_dir)
            
            # Re-generate the prompt string cleanly using the dynamic variables checker method
            self.prompt_string = self._generate_dynamic_prompt()
            
            self.text_area.insert("end", f"\n\n[Terminal Info] Synced to workspace folder: {os.path.basename(self.current_dir)}")
            self._print_prompt()
        except:
            pass
