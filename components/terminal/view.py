"""
SublimeLight - Integrated Terminal Component View
Provides a toggleable command prompt panel shell inside a CustomTkinter textbox frame
safely backed by a real-time thread-safe queue polling shell process engine.
Fully secured against text repetitions, cursor bleeding, and coordinate overlaps.
"""

import os
import queue
import customtkinter as ctk
from .shell_process import ShellProcessEngine

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
            self.header_frame, text="TERMINAL (persistent cmd proxy)", 
            font=("Arial", 10, "bold"), text_color="#75715E"
        )
        self.title_lbl.pack(side="left", padx=15)

        # 2. Command Display/Input Area Text Container
        self.text_area = ctk.CTkTextbox(
            self, font=("Consolas", 12), fg_color="#111111", 
            text_color="#A9FFB2", border_width=0, corner_radius=0
        )
        self.text_area.pack(side="bottom", fill="both", expand=True)

        self.current_dir = os.path.normpath(os.getcwd())
        self.command_start_index = "1.0"

        # Welcome baseline title text
        self.text_area.insert("end", "=== SUBLIMELIGHT INTEGRATED TERMINAL SHELL ===\nType commands natively. Press Ctrl+Shift to toggle visibility.\n")

        # 3. THREAD-SAFE QUEUE SYSTEM ASRESEMBLY
        self.output_queue = queue.Queue()
        self.shell = ShellProcessEngine(self.current_dir, self.output_queue)

        # Bind Key, Click, and Entry Hook protocols
        self.text_area.bind("<Return>", self._on_enter_command)
        self.text_area.bind("<Key>", self._restrict_cursor_bounds)
        self.text_area.bind("<Button-1>", self._enforce_active_input_focus)
        self.text_area.bind("<ButtonRelease-1>", self._enforce_active_input_focus)

        # Start periodic queue monitoring loops straight on CustomTkinter's clock
        self._process_terminal_queue()

    def _process_terminal_queue(self):
        """Monitors the thread-safe queue and flushes chars to the UI, auto-updating markers cleanly."""
        has_new_content = False
        
        while not self.output_queue.empty():
            try:
                char = self.output_queue.get_nowait()
                self.text_area.insert("end", char)
                has_new_content = True
            except queue.Empty:
                break

        if has_new_content:
            self.text_area.see("end")
            self.text_area.mark_set("insert", "end")
            # FIXED: Auto-calculate exactly where shell outputs stop and your input begins!
            self.command_start_index = self.text_area.index("end-1c")

        # Re-schedule the loop iteration task exactly every 10ms natively
        self.after(10, self._process_terminal_queue)

    def _on_enter_command(self, event):
        """Extracts written text directly using the verified prompt indices and routes it down the pipe."""
        command_raw = self.text_area.get(self.command_start_index, "end-1c").strip()
        
        if command_raw.lower() in ("clear", "cls"):
            self.text_area.delete("3.0", "end")
            self.shell.send_input("\n")
            return "break"

        # Direct-pipe input string straight into the stateful sub-process stdin
        self.shell.send_input(command_raw)
        return None  # Let Tkinter append its native linebreak character normally

    def _restrict_cursor_bounds(self, event):
        """Keeps the typing insertion point locked safely ahead of prompt boundary metrics."""
        current_insert = self.text_area.index("insert")
        
        if event.keysym in ("BackSpace", "Left"):
            if self.text_area.compare(current_insert, "<=", self.command_start_index):
                return "break"
                
        if len(event.char) > 0 and event.keysym not in ("Control_L", "Control_R", "Shift_L", "Shift_R"):
            if self.text_area.compare(current_insert, "<", self.command_start_index):
                self.text_area.mark_set("insert", "end")

    def _enforce_active_input_focus(self, event):
        """Bounces insertion indices back down ahead of active prompt marks on click gestures."""
        self.after(1, self._snap_cursor_to_valid_bounds)

    def _snap_cursor_to_valid_bounds(self):
        try:
            current_insert = self.text_area.index("insert")
            if self.text_area.compare(current_insert, "<", self.command_start_index):
                self.text_area.mark_set("insert", "end")
        except:
            pass

    def sync_workspace_directory(self, folder_path):
        """Dynamic hook that instantly forces the shell to change its directory focus."""
        if not folder_path or not os.path.exists(folder_path):
            return
            
        self.current_dir = os.path.normpath(os.path.abspath(folder_path))
        self.shell.current_dir = self.current_dir
        
        # Change running process directory instantly
        self.shell.send_input(f'cd /d "{self.current_dir}"')
        
        # AUTO-ACTIVATION CHECK: See if a local virtual environment script path exists
        venv_activate_bat = os.path.join(self.current_dir, "venv", "Scripts", "activate.bat")
        
        if os.path.exists(venv_activate_bat):
            self.shell.send_input(f'"{venv_activate_bat}"')
        else:
            self.shell.send_input("\n")
