import threading
import tkinter as tk
from tkinter import ttk
import logging
import sys
from pathlib import Path
import os

from utils.logging_setup import setup_console_logging
from utils.chess_resources_manager import setup_resources

# Initialize Logging
setup_console_logging()
logger = logging.getLogger("main")

script_dir = Path(__file__).resolve().parent
project_dir = script_dir.parent

os.chdir(script_dir)

if not setup_resources(script_dir, project_dir):
    logger.error("Resource setup failed")
    sys.exit(1)

from auto_mode import auto_move_loop
from executor import (
    capture_screenshot_in_memory,
    did_my_piece_move,
    expend_fen_row,
    get_best_move,
    cleanup_stockfish,
    initialize_stockfish_at_startup,
    get_current_fen,
    is_castling_possible,
    move_cursor_to_button,
    process_move,
    store_board_positions,
    update_fen_castling_rights,
    verify_move,
    chess_notation_to_index,
    execute_normal_move
)
from gui.new_app import ChessPilotGUI
from gui.shortcuts import bind_shortcuts
import time
from board_detection import get_positions, get_fen_from_position
from board_detection.side_detector import detect_side_from_fen
from utils.speech import speak, get_piece_name

class ChessPilot:
    def __init__(self, root):
        logger.info("Initializing ChessPilot application")
        self.root = root
        self.gui = ChessPilotGUI(master=root)

        # Game state variables
        self.color_indicator = None
        self.last_fen = ""
        self.last_fen_by_color = {'w': None, 'b': None}
        self.board_positions = {}
        
        # Link GUI variables to the backend
        self.auto_mode_var = self.gui.autoplay_var
        self.best_move_var = self.gui.best_move_var
        self.speech_volume_var = self.gui.volume_var
        self.speech_mute_var = self.gui.mute_var
        self.transparency_var = self.gui.transparency_var
        self.side_var = self.gui.side_var
        self.execution_mode_var = self.gui.execution_mode_var

        # Bind GUI events
        self.gui.play_button.config(command=self.process_move_thread)
        self.gui.flip_button.config(command=self.flip_board)
        self.gui.autoplay_check.config(command=self.toggle_auto_mode)
        self.gui.transparency_slider.config(command=self.set_transparency)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        bind_shortcuts(self)
        self.root.focus_set()
        logger.info("ChessPilot UI initialized")

        # Initialize Stockfish at startup
        if not initialize_stockfish_at_startup():
            logger.warning("Stockfish initialization failed at startup - will retry when needed")
        
        # Start the best move update loop
        threading.Thread(target=self.update_best_move_loop, daemon=True).start()

        # Start auto-detection
        threading.Thread(target=self.start_auto_detection, daemon=True).start()

    def _auto_detect_side(self, frames):
        """
        Captures frames until a valid FEN is extracted to determine the player's side.
        """
        logger.info("Attempting to auto-detect side...")
        while True:
            screenshot = self.capture_board_screenshot()
            if screenshot:
                frames.append(screenshot)
                boxes, _, _ = get_positions(screenshot)
                if boxes:
                    _, _, _, fen = get_fen_from_position('w', boxes) # Assume white to get a valid FEN
                    if fen:
                        # Detect side from piece placement, then get active color
                        side = detect_side_from_fen(fen)
                        _, _, _, fen_with_correct_side = get_fen_from_position(side, boxes)
                        active_color = fen_with_correct_side.split()[1]
                        return active_color
            time.sleep(0.3) # Wait before retrying

    def start_auto_detection(self):
        self.update_status("Checking for chessboard on screen...")
        side = self._auto_detect_side([])
        if side:
            self.update_status(f"Detected side: {'White' if side == 'w' else 'Black'}")
            self.side_var.set(side)
            self.color_indicator = side
        else:
            self.update_status("Could not detect chessboard. Please position the board on the screen.")

    def on_closing(self):
        """Handle application closing."""
        logger.info("Application closing - cleaning up Stockfish process")
        cleanup_stockfish()
        self.root.destroy()
        
    # def log_button_sizes(self):
    #     w_w = self.btn_white.winfo_width()
    #     w_h = self.btn_white.winfo_height()
    #     b_w = self.btn_black.winfo_width()
    #     b_h = self.btn_black.winfo_height()
    #     logger.debug(f"[SIZE DEBUG] White button size: {w_w}×{w_h}")
    #     logger.debug(f"[SIZE DEBUG] Black button size: {b_w}×{b_h}")

    def update_last_fen_for_color(self, fen: str):
        parts = fen.split()
        placement, active_color = parts[0], parts[1]
        self.last_fen_by_color[active_color] = placement
        logger.debug(f"Updated last FEN for {active_color}: {placement}")

    def flip_board(self):
        current_side = self.side_var.get()
        new_side = 'b' if current_side == 'w' else 'w'
        self.side_var.set(new_side)
        self.color_indicator = new_side
        self.update_status(f"Flipped side to {'White' if new_side == 'w' else 'Black'}")

    def update_status(self, message):
        logger.debug(f"Status update: {message.strip()}")
        self.gui.status_var.set(message)
        self.root.update_idletasks()

    def set_transparency(self, value):
        self.root.attributes("-alpha", value)

    def toggle_auto_mode(self):
        if self.auto_mode_var.get():
            logger.info("Auto mode enabled")
            self.gui.play_button.config(state=tk.DISABLED)
            threading.Thread(target=auto_move_loop, args=(self,), daemon=True).start()
        else:
            logger.info("Auto mode disabled")
            self.gui.play_button.config(state=tk.NORMAL)

    def process_move_thread(self):
        logger.info("Play Next Move button pressed; starting process_move thread")
        threading.Thread(
            target=process_move,
            args=(
                self.root,
                self.color_indicator,
                self.auto_mode_var,
                self.board_positions,
                self.update_status,
                self.update_last_fen_for_color,
                self.last_fen_by_color,
            ),
            daemon=True,
        ).start()

    def capture_board_screenshot(self):
        logger.debug("Capturing board screenshot via wrapper")
        return capture_screenshot_in_memory(self.root, self.auto_mode_var)

    def convert_move_to_indices(self, move: str):
        logger.debug(f"Converting move to indices: {move}")
        return chess_notation_to_index(
            self.color_indicator,
            self.root,
            self.auto_mode_var,
            move
        )

    def relocate_cursor_to_play_button(self):
        logger.debug("Relocating cursor to Play button via wrapper")
        move_cursor_to_button(self.root, self.auto_mode_var, self.btn_play)

    def expand_fen_row(self, row: str):
        logger.debug(f"Expanding FEN row: {row}")
        return expend_fen_row(row)

    def check_castling(self, fen: str):
        result = is_castling_possible(fen, self.color_indicator, "kingside") or \
                 is_castling_possible(fen, self.color_indicator, "queenside")
        logger.debug(f"Check castling possibility for '{fen}': {result}")
        return result

    def adjust_castling_fen(self, fen: str):
        logger.debug(f"Adjusting castling rights for FEN: {fen}")
        # The new logic will always use the FEN as is, and let the engine decide about castling.
        return fen

    def check_move_validity(self, before_fen: str, after_fen: str, move: str):
        logger.debug(f"Verifying move validity: {move}")
        return did_my_piece_move(self.color_indicator, before_fen, after_fen, move)

    def play_normal_move(self, move: str, mate_flag: bool, expected_fen: str):
        logger.debug(f"Playing normal move via wrapper: {move}")

        if not self.auto_mode_var.get():
            piece = self._get_piece_at_square(move[:2])
            piece_name = get_piece_name(piece)
            speak(f"Move {piece_name} from {move[:2]} to {move[2:]}", self.speech_volume_var.get(), self.speech_mute_var.get())

        return execute_normal_move(
            self.board_positions,
            self.color_indicator,
            move,
            mate_flag,
            expected_fen,
            self.root,
            self.auto_mode_var,
            self.update_status,
            self.btn_play,
            self.execution_mode_var.get()
        )

    def _get_piece_at_square(self, square):
        fen = self.last_fen_by_color.get(self.color_indicator)
        if not fen:
            return ''

        file_map = {chr(ord('a') + i): i for i in range(8)}
        rank_map = {str(i + 1): 7 - i for i in range(8)}

        file = square[0]
        rank = square[1]

        col = file_map.get(file)
        row = rank_map.get(rank)

        if col is None or row is None:
            return ''

        rows = fen.split('/')
        fen_row = rows[row]

        current_col = 0
        for char in fen_row:
            if char.isdigit():
                current_col += int(char)
            else:
                if current_col == col:
                    return char
                current_col += 1
        return ''

    def query_best_move(self, fen: str):
        logger.debug(f"Querying best move for FEN: {fen}")
        return get_best_move(
            22,  # Hardcoded depth for maximum strength
            fen,
            self.root,
            self.auto_mode_var
        )

    def read_current_fen(self):
        logger.debug("Reading current FEN via wrapper")
        return get_current_fen(self.color_indicator)

    def store_positions(self, x: int, y: int, size: int):
        logger.debug(f"Storing board positions: x={x}, y={y}, size={size}")
        store_board_positions(self.board_positions, x, y, size)

    def verify_move_wrapper(self, before_fen: str, expected_fen: str, attempts_limit: int = 3):
        logger.debug(f"Verifying move via wrapper; expected FEN: {expected_fen}")
        return verify_move(
            self.color_indicator,
            before_fen,
            expected_fen,
            attempts_limit
        )

    def update_best_move_loop(self):
        while True:
            if self.color_indicator and not self.auto_mode_var.get():
                fen = self.read_current_fen()
                if fen:
                    best_move, _, _ = self.query_best_move(fen)
                    if best_move:
                        self.best_move_var.set(f"Best Move: {best_move}")
                        if not self.auto_mode_var.get():
                            piece = self._get_piece_at_square(best_move[:2])
                            piece_name = get_piece_name(piece)
                            speak(f"Move {piece_name} from {best_move[:2]} to {best_move[2:]}", self.speech_volume_var.get(), self.speech_mute_var.get())
            time.sleep(1)

if __name__ == "__main__":

    logger.info("Stockfish and ONNX model setup completed successfully")
    logger.info("Starting ChessPilot main loop")
    root = tk.Tk()
    app = ChessPilot(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        logger.info("Exiting APP")
        cleanup_stockfish()  # Also cleanup on keyboard interrupt
        root.destroy()
    logger.info("ChessPilot application closed")