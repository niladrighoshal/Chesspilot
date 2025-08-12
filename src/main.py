import sys
import threading
import time
import logging
import os
import tkinter as tk
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
        self.gui = ModernTkinterApp(master=root)

        self.is_closing = False
        self.is_capturing = False
        self.board_positions = {}
        self.last_fen_by_color = {'w': None, 'b': None}
        
        self.color_indicator = 'w'
        self.auto_mode = False
        self.drag_mode = True

        self.setup_connections()

        if not initialize_stockfish_at_startup():
            self.update_status("Stockfish initialization failed.")

        threading.Thread(target=self.auto_detection_thread, daemon=True).start()
        threading.Thread(target=self.best_move_thread, daemon=True).start()

    def setup_connections(self):
        self.gui.capture_button.config(command=self.toggle_capture)
        self.gui.play_button.config(command=self.process_move_thread)
        # The toggles are connected via variables, but commands can be added if needed
        self.gui.volume_var.trace_add("write", self.update_volume)
        self.gui.transparency_var.trace_add("write", self.set_transparency)
        self.gui.side_var.trace_add("write", self.flip_board)
        self.gui.drag_click_var.trace_add("write", self.toggle_drag_click)
        self.gui.autoplay_var.trace_add("write", self.toggle_auto_mode)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_status(self, text):
        self.gui.status_var.set(text)

    def update_best_move(self, text):
        self.gui.best_move_var.set(text)

    def toggle_capture(self):
        self.is_capturing = not self.is_capturing
        state = "ON" if self.is_capturing else "OFF"
        self.update_status(f"Screen Capture: {state}")
        self.gui.capture_button.config(text="■" if self.is_capturing else "▶", fg="red" if self.is_capturing else "#00FF00")

    def auto_detection_thread(self):
        while not self.is_closing:
            if self.is_capturing and self.color_indicator is None:
                self.update_status("Detecting side...")
                fen = get_current_fen('w')
                if fen:
                    side = detect_side_from_fen(fen)
                    self.color_indicator = side
                    self.gui.side_var.set(side)
                    self.update_status(f"Detected side: {'White' if side == 'w' else 'Black'}")
            time.sleep(1)

    def best_move_thread(self):
        while not self.is_closing:
            if self.is_capturing and self.color_indicator and not self.auto_mode:
                fen = get_current_fen(self.color_indicator)
                if fen:
                    move, _, _ = get_best_move(22, fen)
                    if move:
                        self.update_best_move(f"Best Move: {move}")
                        if not self.gui.mute_var.get():
                            piece = get_piece_name(get_piece_at_square(fen, move[:2]))
                            speak(f"Move {piece} from {move[:2]} to {move[2:]}", self.gui.volume_var.get()/100)
            time.sleep(2)

    def process_move_thread(self):
        if self.is_capturing:
            threading.Thread(target=process_move, args=(self,), daemon=True).start()
        else:
            self.update_status("Enable screen capture first.")

    def toggle_auto_mode(self, *args):
        self.auto_mode = self.gui.autoplay_var.get()
        self.gui.play_button.config(state=tk.DISABLED if self.auto_mode else tk.NORMAL)
        if self.auto_mode:
            threading.Thread(target=auto_move_loop, args=(self,), daemon=True).start()

    def flip_board(self, *args):
        self.color_indicator = self.gui.side_var.get()
        self.update_status(f"Side set to {'White' if self.color_indicator == 'w' else 'Black'}")

    def toggle_drag_click(self, *args):
        self.drag_mode = self.gui.drag_click_var.get() == "drag"

    def update_volume(self, *args):
        # The variable is already linked to the slider
        pass

    def set_transparency(self, *args):
        self.root.attributes("-alpha", self.gui.transparency_var.get() / 100)

    def on_closing(self):
        self.is_closing = True
        cleanup_stockfish()
        self.root.destroy()

def get_piece_at_square(fen, square):
    # This is a helper function that should probably be in a different file
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
    root.mainloop()

if __name__ == "__main__":
    main()
