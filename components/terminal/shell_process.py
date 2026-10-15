"""
SublimeLight - Terminal Shell Process Engine
Manages a stateful, persistent cmd.exe background process thread matrix 
backed by a thread-safe multi-stream character queue.
"""

import subprocess
import threading
import queue

class ShellProcessEngine:
    def __init__(self, initial_dir, output_queue):
        self.current_dir = initial_dir
        self.output_queue = output_queue
        self.process = None
        self.start_shell()

    def start_shell(self):
        """Launches a single long-running background CMD shell with detached pipeline streams."""
        try:
            # Fully synchronized sub-process engine instantiation mapping stdout and stderr channels
            self.process = subprocess.Popen(
                ["cmd.exe"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                shell=True,
                cwd=self.current_dir,
                creationflags=subprocess.CREATE_NO_WINDOW  # Safe background pipe execution
            )
            
            # Instantiated dedicated thread workers to pull stdout and stderr concurrently
            threading.Thread(target=self._stream_reader_loop, args=(self.process.stdout,), daemon=True).start()
            threading.Thread(target=self._stream_reader_loop, args=(self.process.stderr,), daemon=True).start()
            
            # Sync initialization views cleanly
            self.send_input("\n")
        except Exception as e:
            self.output_queue.put(f"Shell Process Initialization Engine Failure: {e}\n")

    def _stream_reader_loop(self, stream):
        """Asynchronous reader thread collecting character blocks continuously without locking the GUI."""
        while True:
            try:
                char = stream.read(1)
                if not char:
                    break
                self.output_queue.put(char)
            except:
                break

    def send_input(self, command_str):
        """Pushes string data blocks down into the persistent subprocess pipeline channel."""
        if self.process and self.process.stdin:
            try:
                self.process.stdin.write(command_str + "\n")
                self.process.stdin.flush()
            except:
                pass
