import pyautogui
import logging
from tkinter import messagebox
import os
import time
from .is_wayland import is_wayland
from wayland_capture.wayland import WaylandInput
from executor.chess_notation_to_index import chess_notation_to_index
from executor.move_cursor_to_button import move_cursor_to_button
import random

if os.name == 'nt':
    import win32api
    import win32con


# Logger setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def _get_piece_start_and_end_pos(color_indicator, move, board_positions, root, auto_mode_var):
    """A helper function to get the start and end positions for a move."""
    start_idx, end_idx = chess_notation_to_index(color_indicator, root, auto_mode_var, move)
    if not start_idx or not end_idx:
        logger.warning("Invalid notation to index mapping; move aborted")
        return None, None

    try:
        start_pos = board_positions[start_idx]
        end_pos = board_positions[end_idx]
        logger.debug(f"Start: {start_idx} -> {start_pos}, End: {end_idx} -> {end_pos}")
        return start_pos, end_pos
    except KeyError:
        logger.error("Could not map move to board positions")
        root.after(0, lambda: messagebox.showerror("Error", "Could not map move to board positions"))
        auto_mode_var.set(False)
        return None, None

def drag_piece(color_indicator, move, board_positions, auto_mode_var, root, btn_play, drag_offset=10):
    logger.info(f"Attempting drag move: {move}")
    start_pos, end_pos = _get_piece_start_and_end_pos(color_indicator, move, board_positions, root, auto_mode_var)
    if not start_pos or not end_pos:
        return

    start_x, start_y = start_pos
    end_x, end_y = end_pos

    # Add random offsets for a more human-like drag
    start_x += random.randint(-drag_offset, drag_offset)
    start_y += random.randint(-drag_offset, drag_offset)
    end_x += random.randint(-drag_offset, drag_offset)
    end_y += random.randint(-drag_offset, drag_offset)

    try:
        if os.name == 'nt':
            logger.debug("Using win32api for Windows input (drag simulation)")
            win32api.SetCursorPos((int(start_x), int(start_y)))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(random.uniform(0.05, 0.15))
            win32api.SetCursorPos((int(end_x), int(end_y)))
            time.sleep(random.uniform(0.05, 0.15))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        elif is_wayland():
            logger.debug("Using Wayland input method")
            client = WaylandInput()
            client.swipe(int(start_x), int(start_y), int(end_x), int(end_y), time.uniform(0.1, 0.3))
        else:
            logger.debug("Using PyAutoGUI for input")
            pyautogui.moveTo(start_x, start_y, duration=random.uniform(0.1, 0.3))
            pyautogui.mouseDown()
            pyautogui.moveTo(end_x, end_y, duration=random.uniform(0.1, 0.4))
            pyautogui.mouseUp()
        logger.info("Drag move simulated successfully")
    except Exception as e:
        logger.error(f"Failed to drag piece: {e}")
        root.after(0, lambda err=e: messagebox.showerror("Error", f"Failed to drag piece: {str(err)}"))
        auto_mode_var.set(False)
        return

    if not auto_mode_var.get():
        logger.debug("Auto mode off after move; restoring cursor to Play button")
        root.after(0, lambda: move_cursor_to_button(root, auto_mode_var, btn_play))

def get_piece_at_square(fen, square):
    file_map = {chr(ord('a') + i): i for i in range(8)}
    rank_map = {str(i + 1): 7 - i for i in range(8)}

    file = square[0]
    rank = square[1]

    col = file_map.get(file)
    row = rank_map.get(rank)

    if col is None or row is None:
        return None

    rows = fen.split(' ')[0].split('/')
    fen_row = rows[row]

    current_col = 0
    for char in fen_row:
        if char.isdigit():
            current_col += int(char)
        else:
            if current_col == col:
                return char
            current_col += 1
    return None

def is_promotion(fen, move):
    start_square = move[:2]
    end_square = move[2:]
    piece = get_piece_at_square(fen, start_square)

    if piece is None:
        return False

    if piece.lower() != 'p':
        return False

    if piece.islower() and end_square[1] == '1': # Black pawn
        return True

    if piece.isupper() and end_square[1] == '8': # White pawn
        return True

    return False

def click_piece(color_indicator, move, board_positions, auto_mode_var, root, btn_play, click_offset=10, delay=0.5):
    logger.info(f"Attempting click move: {move}")
    start_pos, end_pos = _get_piece_start_and_end_pos(color_indicator, move, board_positions, root, auto_mode_var)
    if not start_pos or not end_pos:
        return

    start_x, start_y = start_pos
    end_x, end_y = end_pos

    # Add random offsets for a more human-like click
    start_x += random.randint(-click_offset, click_offset)
    start_y += random.randint(-click_offset, click_offset)
    end_x += random.randint(-click_offset, click_offset)
    end_y += random.randint(-click_offset, click_offset)

    try:
        if os.name == 'nt':
            logger.debug("Using win32api for Windows input (click simulation)")
            win32api.SetCursorPos((int(start_x), int(start_y)))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            time.sleep(delay)
            win32api.SetCursorPos((int(end_x), int(end_y)))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        elif is_wayland():
            logger.debug("Using Wayland input method for click")
            client = WaylandInput()
            client.click(int(start_x), int(start_y))
            time.sleep(delay)
            client.click(int(end_x), int(end_y))
        else:
            logger.debug("Using PyAutoGUI for input")
            pyautogui.click(start_x, start_y)
            time.sleep(delay)
            pyautogui.click(end_x, end_y)
        logger.info("Click move simulated successfully")
    except Exception as e:
        logger.error(f"Failed to click piece: {e}")
        root.after(0, lambda err=e: messagebox.showerror("Error", f"Failed to click piece: {str(err)}"))
        auto_mode_var.set(False)
        return

    if not auto_mode_var.get():
        logger.debug("Auto mode off after move; restoring cursor to Play button")
        root.after(0, lambda: move_cursor_to_button(root, auto_mode_var, btn_play))
