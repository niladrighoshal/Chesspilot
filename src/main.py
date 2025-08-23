import sys
import threading
import time
import logging
import os
import tkinter as tk
from queue import Queue, Empty
import random

from gui.modern_tkinter_app import ModernTkinterApp
from utils.logging_setup import setup_console_logging
from utils.chess_resources_manager import setup_resources
from auto_mode import auto_move_loop
from executor import (
    capture_screenshot_in_memory,
    get_best_move,
    cleanup_stockfish,
    initialize_stockfish_at_startup,
    get_current_fen,
    process_move,
)
from board_detection import get_positions, get_fen_from_position
from board_detection.side_detector import detect_side_from_fen
from utils.speech import speak, get_piece_name

class ChessPilot:
    def __init__(self, root):
        self.root = root

        # State Variables
        self.is_closing = False
        self.is_capturing = False
        self.board_positions = {}
        self.last_fen_by_color = {'w': None, 'b': None}
        self.color_indicator = None
        self.auto_mode = False
        self.drag_mode = True
        self.mute = False
        self.volume = 0.1
        self.move_count = 0
        self.best_move_cache = None

        # GUI Variables
        self.status_var = tk.StringVar(value="Initializing...")
        self.best_move_var = tk.StringVar(value="Best Move: ...")
        self.side_state_var = tk.StringVar(value="White")
        self.drag_click_state_var = tk.StringVar(value="Drag")
        self.autoplay_state_var = tk.StringVar(value="OFF")
        self.mute_state_var = tk.StringVar(value="ON")

        self.gui = ModernTkinterApp(master=root, app_logic=self)
        self.queue = Queue()

        if not initialize_stockfish_at_startup():
            self.update_status("Stockfish initialization failed.")

        self.root.after(100, self.process_queue)
        self.setup_key_bindings()
        self.toggle_capture()

    def setup_key_bindings(self):
        self.root.bind('<space>', lambda e: self.play_best_move())
        self.root.bind('<Key-m>', lambda e: self.gui.mute_toggle.invoke())
        self.root.bind('<Key-a>', lambda e: self.gui.autoplay_toggle.invoke())
        self.root.bind('<Control_L>', lambda e: self.gui.drag_click_toggle.invoke())
        self.root.bind('<Control_R>', lambda e: self.gui.drag_click_toggle.invoke())

    def process_queue(self):
        try:
            message = self.queue.get_nowait()
            msg_type = message.get("type")
            payload = message.get("payload")

            if msg_type == "status_update":
                self.update_status(payload)
            elif msg_type == "side_detected":
                self.color_indicator = payload
                self.gui.side_toggle.on = (payload == 'b')
                self.gui.side_toggle._redraw()
                self.update_status(f"Side detected: {'White' if payload == 'w' else 'Black'}. Ready.")
                self.start_best_move_thread()
            elif msg_type == "best_move_update":
                self.best_move_cache = payload
                self.gui.best_move_var.set(f"Best Move: {payload}")

        except Empty:
            pass
        finally:
            if not self.is_closing:
                self.root.after(100, self.process_queue)

    def update_status(self, text):
        self.status_var.set(text)

    def toggle_capture(self):
        self.is_capturing = not self.is_capturing
        self.gui.capture_button.config(text="■" if self.is_capturing else "▶", fg="red" if self.is_capturing else "#00FF00")
        if self.is_capturing:
            self.update_status("Capture ON. Detecting board...")
            if self.color_indicator is None:
                threading.Thread(target=self.auto_detection_thread, daemon=True).start()
            else:
                self.start_best_move_thread()
        else:
            self.update_status("Capture OFF.")
            self.best_move_cache = None
            self.gui.best_move_var.set("Best Move: ...")

    def auto_detection_thread(self):
        fen = None
        for _ in range(10):
            if not self.is_capturing: return
            screenshot = capture_screenshot_in_memory()
            if screenshot:
                boxes, _, _ = get_positions(screenshot)
                if boxes:
                    _, _, _, fen = get_fen_from_position('w', boxes)
                    if fen: break
            time.sleep(0.5)

        if fen:
            side = detect_side_from_fen(fen)
            self.queue.put({"type": "side_detected", "payload": side})
        else:
            self.queue.put({"type": "status_update", "payload": "Board not found. Pausing capture."})
            self.is_capturing = False
            self.gui.capture_button.config(text="▶", fg="#00FF00")

    def start_best_move_thread(self):
        if not hasattr(self, "best_move_thread_instance") or not self.best_move_thread_instance.is_alive():
            self.best_move_thread_instance = threading.Thread(target=self.best_move_thread, daemon=True)
            self.best_move_thread_instance.start()

    def best_move_thread(self):
        while not self.is_closing and self.is_capturing:
            if self.color_indicator and not self.auto_mode:
                fen = get_current_fen(self.color_indicator)
                if fen:
                    move, _, _ = get_best_move(22, fen)
                    if move and move != self.best_move_cache:
                        self.queue.put({"type": "best_move_update", "payload": move})
            time.sleep(2)

    def play_best_move(self):
        if self.best_move_cache:
            if not self.mute:
                self.speak_move(self.best_move_cache)
            self.process_move_thread(self.best_move_cache)
        else:
            self.update_status("No best move available to play.")

    def process_move_thread(self, move):
        if self.is_capturing:
            self.move_count += 1
            threading.Thread(target=process_move, args=(self, move), daemon=True).start()
        else:
            self.update_status("Enable screen capture first.")

    def toggle_auto_mode(self, state):
        self.auto_mode = state
        self.gui.play_button.config(state=tk.DISABLED if self.auto_mode else tk.NORMAL)
        self.autoplay_state_var.set("ON" if self.auto_mode else "OFF")
        if self.auto_mode and self.is_capturing:
            threading.Thread(target=auto_move_loop, args=(self,), daemon=True).start()

    def flip_board(self, state):
        self.color_indicator = 'b' if state else 'w'
        self.side_state_var.set("Black" if self.color_indicator == 'b' else 'White')
        self.update_status(f"Side set to {self.side_state_var.get()}")

    def toggle_drag_click(self, state):
        self.drag_mode = not state
        self.drag_click_state_var.set("Click" if self.drag_mode else "Drag")

    def toggle_mute(self, state):
        self.mute = state
        self.mute_state_var.set("OFF" if self.mute else "ON")

    def set_volume(self, value):
        self.volume = float(value) / 100

    def set_transparency(self, value):
        self.root.attributes("-alpha", float(value) / 100)

    def speak_move(self, move):
        fen = get_current_fen(self.color_indicator)
        if fen:
            piece = get_piece_at_square(fen, move[:2])
            speak(f"Move {get_piece_name(piece)} from {move[:2]} to {move[2:]}", self.volume)

    def on_closing(self):
        self.is_closing = True
        cleanup_stockfish()
        self.root.destroy()

def get_piece_at_square(fen, square):
    file_map = {chr(ord('a') + i): i for i in range(8)}
    rank_map = {str(i + 1): 7 - i for i in range(8)}
    file, rank = square[0], square[1]
    col, row = file_map.get(file), rank_map.get(rank)
    if col is None or row is None: return ''
    fen_row = fen.split(' ')[0].split('/')[row]
    current_col = 0
    for char in fen_row:
        if char.isdigit():
            current_col += int(char)
        else:
            if current_col == col: return char
            current_col += 1
    return ''

def main():
    setup_console_logging()
    if not setup_resources(os.path.dirname(__file__), os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))):
        sys.exit(1)

    root = tk.Tk()
    app = ChessPilot(root)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = screen_width - 400 - random.randint(10, 80)
    y = (screen_height // 2) - 300 + random.randint(-80, 80)
    root.geometry(f'400x600+{x}+{y}')

    root.mainloop()

if __name__ == "__main__":
    main()
