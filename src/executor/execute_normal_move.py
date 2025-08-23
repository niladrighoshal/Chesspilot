import time
import logging
import tkinter as tk
from board_detection import get_positions, get_fen_from_position
from executor.capture_screenshot_in_memory import capture_screenshot_in_memory
from executor.get_current_fen import get_current_fen
from executor.chess_notation_to_index import chess_notation_to_index
from executor.move_executor import drag_piece, click_piece
from executor.did_my_piece_move import did_my_piece_move

logger = logging.getLogger(__name__)

def execute_normal_move(app, move, expected_fen, mate_flag):
    logger.info(f"Attempting move: {move} for {app.color_indicator}")
    max_retries = 3

    for attempt in range(1, max_retries + 1):
        logger.debug(f"[Attempt {attempt}/{max_retries}] Starting move sequence")

        original_fen = get_current_fen(app.color_indicator)
        if not original_fen:
            logger.warning("Could not fetch original FEN, retrying...")
            time.sleep(0.1)
            continue

        start_square, end_square = chess_notation_to_index(move)
        if start_square is None or end_square is None:
            logger.warning("Invalid move indices, retrying...")
            time.sleep(0.1)
            continue

        try:
            start_pos = app.board_positions[start_square]
            end_pos = app.board_positions[end_square]
        except KeyError:
            logger.warning(f"Start or end position not found in board_positions for move {move}. Available keys: {list(app.board_positions.keys())}")
            time.sleep(0.1)
            continue

        execution_mode = "drag" if app.drag_mode else "click"
        if execution_mode == "drag":
            drag_piece(app.color_indicator, move, app.board_positions, app.auto_mode, app.gui, app.gui.play_button)
        else:
            click_piece(app.color_indicator, move, app.board_positions, app.auto_mode, app.gui, app.gui.play_button)
        time.sleep(0.5)

        img = capture_screenshot_in_memory()
        if not img:
            logger.warning("Screenshot failed, retrying...")
            continue

        boxes, _, _ = get_positions(img)
        if not boxes:
            logger.warning("Board detection failed, retrying...")
            continue

        try:
            _, _, _, current_fen = get_fen_from_position(app.color_indicator, boxes)
        except ValueError as e:
            logger.warning(f"FEN extraction error: {e}, retrying...")
            continue

        if did_my_piece_move(app.color_indicator, original_fen, current_fen, move):
            status = f"Move Played: {move}"
            logger.info(f"Move executed successfully: {move}")

            if mate_flag:
                status += "\nCheckmate!"
                app.auto_mode = False
                app.gui.autoplay_var.set(False)

            app.update_status(status)
            return True

    logger.error(f"Move {move} failed after {max_retries} attempts")
    app.update_status(f"Move failed to register: {move}")
    app.auto_mode = False
    app.gui.autoplay_var.set(False)
    return False
