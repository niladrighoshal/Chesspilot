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
from gui.set_window_icon import set_window_icon
from gui.create_widget import create_widgets
from gui.shortcuts import handle_esc_key, bind_shortcuts
from gui.button_and_checkboxes import (
    color_button,
    action_button,
    castling_checkboxes
)
from utils.speech import speak, get_piece_name

class ChessPilot:
    def __init__(self, root):
        logger.info("Initializing ChessPilot application")
        self.root = root
        self.root.title("ChessPilot")
        self.root.geometry("350x350")
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Game state variables
        self.color_indicator = None
        self.last_fen = ""
        self.last_fen_by_color = {'w': None, 'b': None}
        self.auto_mode_var = tk.BooleanVar(value=False)
        self.board_positions = {}
        self.best_move_var = tk.StringVar()

        # Speech settings
        self.speech_volume_var = tk.DoubleVar(value=0.5)
        self.speech_mute_var = tk.BooleanVar(value=False)

        # Screenshot delay (0.0 to 1.0 seconds)
        self.screenshot_delay_var = tk.DoubleVar(value=0.4)

        # GUI settings
        self.transparency_var = tk.DoubleVar(value=0.5)

        # Board cropping parameters (unused until you set them)
        self.chessboard_x = None
        self.chessboard_y = None
        self.square_size = None

        # UI color scheme
        self.bg_color = "#2D2D2D"
        self.frame_color = "#373737"
        self.accent_color = "#4CAF50"
        self.text_color = "#FFFFFF"
        self.hover_color = "#45a049"
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TScale", troughcolor=self.frame_color, background=self.bg_color)
        self.style.configure("TCheckbutton", background=self.bg_color, foreground=self.text_color)
        
        set_window_icon(self)
        create_widgets(self)
        bind_shortcuts(self)

        # Log initial window size for debugging
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        logger.debug(f"Initial window size: {width}x{height}")
        

        self.root.bind('<Escape>', self.take_esc_key)
        self.root.focus_set()
        logger.info("ChessPilot UI initialized")
        
        # Initialize Stockfish at startup
        if not initialize_stockfish_at_startup():
            logger.warning("Stockfish initialization failed at startup - will retry when needed")
        
        # Start the best move update loop
        threading.Thread(target=self.update_best_move_loop, daemon=True).start()

    def on_closing(self):
        """Handle application closing."""
        logger.info("Application closing - cleaning up Stockfish process")
        cleanup_stockfish()
        self.root.destroy()
        
    # Handle ESC key to return to color selection
    def take_esc_key(self, event=None):
        if self.color_indicator is not None:
            handle_esc_key(self, event)
        
    # def log_button_sizes(self):
    #     w_w = self.btn_white.winfo_width()
    #     w_h = self.btn_white.winfo_height()
    #     b_w = self.btn_black.winfo_width()
    #     b_h = self.btn_black.winfo_height()
    #     logger.debug(f"[SIZE DEBUG] White button size: {w_w}×{w_h}")
    #     logger.debug(f"[SIZE DEBUG] Black button size: {b_w}×{b_h}")

    def create_color_button(self, parent, text, color):
        return color_button(self, parent, text, color)

    def create_action_button(self, parent, text, command):
        return action_button(self, parent, text, command)
        
    def create_castling_checkboxes(self):
        castling_checkboxes(self)

    def update_last_fen_for_color(self, fen: str):
        parts = fen.split()
        placement, active_color = parts[0], parts[1]
        self.last_fen_by_color[active_color] = placement
        logger.debug(f"Updated last FEN for {active_color}: {placement}")

    def set_color(self, color):
        logger.info(f"Color selected: {'White' if color == 'w' else 'Black'}")
        self.color_indicator = color
        self.color_frame.pack_forget()
        self.main_frame.pack(expand=True, fill=tk.BOTH)
        self.btn_play.config(state=tk.NORMAL)
        self.update_status(f"\nPlaying as {'White' if color == 'w' else 'Black'}")

    def flip_board(self):
        if self.color_indicator == 'w':
            self.set_color('b')
        else:
            self.set_color('w')

    def update_status(self, message):
        logger.debug(f"Status update: {message.strip()}")
        self.status_label.config(text=message)
        self.root.update_idletasks()

    def set_transparency(self, value):
        self.root.attributes("-alpha", value)

    def process_move_thread(self):
        logger.info("Play Next Move button pressed; starting process_move thread")
        threading.Thread(
            target=process_move,
            args=(
                self.root,
                self.color_indicator,
                self.auto_mode_var,
                self.btn_play,
                self.board_positions,
                self.update_status,
                self.kingside_var,
                self.queenside_var,
                self.update_last_fen_for_color,
                self.last_fen_by_color,
                self.screenshot_delay_var,
            ),
            daemon=True,
        ).start()

    def toggle_auto_mode(self):
        if self.auto_mode_var.get():
            logger.info("Auto mode enabled")
            self.btn_play.config(state=tk.DISABLED)
            # The auto_move_loop will handle initialization and side detection
            threading.Thread(
                target=auto_move_loop,
                args=(
                    self.root,
                    self.color_indicator,
                    self.auto_mode_var,
                    self.btn_play,
                    self.board_positions,
                    self.last_fen_by_color,
                    self.screenshot_delay_var,
                    self.update_status,
                    self.kingside_var,
                    self.queenside_var,
                    self.update_last_fen_for_color
                ),
                daemon=True
            ).start()

        else:
            logger.info("Auto mode disabled")
            self.btn_play.config(state=tk.NORMAL)

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
        return update_fen_castling_rights(
            self.color_indicator,
            self.kingside_var,
            self.queenside_var,
            fen
        )

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