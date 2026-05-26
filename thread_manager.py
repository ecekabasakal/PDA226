"""
thread_manager.py - Background threading for Album Cover Studio

Runs the album generation task in a background thread so the GUI
does not freeze while waiting for API responses.
"""

import threading


class ThreadManager:
    def __init__(self, root):
        self.root = root
        self.pipeline_running = False

    def run_in_background(self, task_function):
        # Runs the full pipeline in a background thread
        self.pipeline_running = True

        def worker():
            try:
                task_function()
            finally:
                self.pipeline_running = False

        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.start()

    def run_parallel(self, task_function):
        # Starts a task in a new thread, returns it so we can .join() later
        thread = threading.Thread(target=task_function)
        thread.daemon = True
        thread.start()
        return thread

    def update_gui(self, callback):
        # Safely schedule a GUI update from a background thread
        self.root.after(0, callback)
