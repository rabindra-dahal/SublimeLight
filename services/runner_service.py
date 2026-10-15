"""
SublimeLight - Runner Infrastructure Service
Handles secure, decoupled background execution routines inside native OS terminals.
"""

import os
import subprocess
import time

class RunnerService:
    @staticmethod
    def execute_script(file_path):
        """Launches code inside an external, fully interactive native console window."""
        if not file_path or not os.path.exists(file_path):
            return
            
        try:
            script_dir = os.path.dirname(file_path)
            script_name = os.path.basename(file_path)
            
            if os.name == 'nt':  # Windows Environment
                # Create a clean temporary launcher script to handle path syntax flawlessly
                bat_path = os.path.join(script_dir, "run_launcher_temp.bat")
                with open(bat_path, "w") as bat_file:
                    bat_file.write(f'@echo off\n')
                    bat_file.write(f'cd /d "{script_dir}"\n')
                    bat_file.write(f'cls\n')
                    bat_file.write(f'echo Running: {script_name}...\n')
                    bat_file.write(f'echo -----------------------------------------\n')
                    bat_file.write(f'python "{script_name}"\n')
                    bat_file.write(f'echo.\n')
                    bat_file.write(f'echo -----------------------------------------\n')
                    bat_file.write(f'echo [Process finished. Press any key to close this terminal...]\n')
                    bat_file.write(f'pause > nul\n')
                
                # Launch the batch script in a real new console window
                process = subprocess.Popen(
                    ["cmd", "/C", bat_path],
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
                
                # Wait for the user to close or finish the script in the background thread,
                # then quietly delete the temporary file so it doesn't clutter their folder.
                def cleanup():
                    process.wait()
                    try:
                        os.remove(bat_path)
                    except:
                        pass
                
                import threading
                threading.Thread(target=cleanup, daemon=True).start()

            else:  # Linux / Unix Platform Fallbacks
                subprocess.Popen(["x-terminal-emulator", "-e", "python3", file_path])
                
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Execution Error", f"Failed initializing background script execution: {e}")
