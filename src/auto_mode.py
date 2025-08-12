import time
import threading
import logging
from collections import deque
import random

from board_detection import get_positions, get_fen_from_position
from executor.capture_screenshot_in_memory import capture_screenshot_in_memory
from executor.process_move import process_move
from executor.processing_sync import processing_event

logger = logging.getLogger(__name__)

def auto_move_loop(app):
    logger.info("Auto move loop started")
    frames = deque(maxlen=10)
    screenshot_interval = 0.3

    color_indicator = app.color_indicator
    opp_color = 'b' if color_indicator == 'w' else 'w'

    last_opponent_move_time = time.time()

    while app.auto_mode and not app.is_closing:
        start_time = time.time()

        if processing_event.is_set():
            time.sleep(screenshot_interval)
            continue

        screenshot = capture_screenshot_in_memory()
        if screenshot:
            frames.append(screenshot)

        if not frames:
            time.sleep(screenshot_interval)
            continue

        latest_frame = frames[-1]
        boxes, midpoints, drag_offset = get_positions(latest_frame)

        if not boxes:
            time.sleep(screenshot_interval)
            continue

        app.board_positions = midpoints

        _, _, _, current_fen = get_fen_from_position(color_indicator, boxes)
        if not current_fen:
            time.sleep(screenshot_interval)
            continue

        placement, active_color = current_fen.split()[:2]

        if active_color == opp_color:
            if _handle_opponent_turn(opp_color, placement, app.last_fen_by_color):
                last_opponent_move_time = time.time()

        elif active_color == color_indicator:
            if _handle_player_turn(opp_color, placement, app.last_fen_by_color):
                delay = _get_realistic_delay(last_opponent_move_time)
                logger.info(f"Waiting for {delay:.2f} seconds before making a move.")
                time.sleep(delay)
                # Directly call process_move in a new thread
                threading.Thread(target=process_move, args=(app,), daemon=True).start()

        elapsed_time = time.time() - start_time
        sleep_time = max(0, screenshot_interval - elapsed_time)
        time.sleep(sleep_time)

    logger.info("Auto move loop finished.")

def _get_realistic_delay(last_opponent_move_time):
    opponent_time = time.time() - last_opponent_move_time
    delay = opponent_time * random.uniform(0.5, 0.8) + random.uniform(0.2, 0.5)
    return max(0.5, min(delay, 5.0))

def _handle_opponent_turn(opp_color, placement, last_fen_by_color):
    old = last_fen_by_color.get(opp_color)
    if old is None or placement != old:
        logger.info("Opponent moved; updating last_fen_by_color[opp_color].")
        last_fen_by_color[opp_color] = placement
        return True
    return False

def _handle_player_turn(opp_color, placement, last_fen_by_color):
    if opp_color not in last_fen_by_color or last_fen_by_color[opp_color] is None:
        return False

    if placement != last_fen_by_color[opp_color]:
        logger.info("Detected genuine opponent move; launching our move.")
        last_fen_by_color[opp_color] = placement
        return True
    return False
