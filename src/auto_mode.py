import time
import threading
import logging
from collections import deque

from board_detection import get_positions, get_fen_from_position
from board_detection.side_detector import detect_side_from_fen
from executor.capture_screenshot_in_memory import capture_screenshot_in_memory
from executor.process_move import process_move
from executor.processing_sync import processing_event

# Logger setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def process_move_thread(
    root,
    color_indicator,
    auto_mode_var,
    btn_play,
    board_positions,
    update_status,
    kingside_var,
    queenside_var,
    update_last_fen_for_color,
    last_fen_by_color,
    screenshot_delay_var,
):
    """
    Starts a new daemon thread that will run process_move().
    """
    logger.info("Starting new thread to process move")
    threading.Thread(
        target=process_move,
        args=(
            root,
            color_indicator,
            auto_mode_var,
            btn_play,
            board_positions,
            update_status,
            kingside_var,
            queenside_var,
            update_last_fen_for_color,
            last_fen_by_color,
            screenshot_delay_var,
        ),
        daemon=True,
    ).start()


def auto_move_loop(
    app
):
    """
    Main auto move loop - coordinates the overall flow.
    """
    logger.info("Auto move loop started")

    # Real-time processing setup
    frames = deque(maxlen=10)
    screenshot_interval = 0.3  # 300 ms

    color_indicator = app.color_indicator
    opp_color = 'b' if color_indicator == 'w' else 'w'
    logger.info(f"Player color: {color_indicator}, Opponent color: {opp_color}")

    # Main processing loop
    _run_real_time_move_detection(
        app.root, color_indicator, opp_color, app.auto_mode_var, app.gui.play_button,
        app.board_positions, app.last_fen_by_color, screenshot_interval,
        app.update_status, app.update_last_fen_for_color,
        frames
    )

    logger.info("Exiting auto_move_loop")

def _run_real_time_move_detection(
    root, color_indicator, opp_color, auto_mode_var, btn_play,
    board_positions, last_fen_by_color, screenshot_interval,
    update_status_callback, update_last_fen_for_color,
    frames
):
    """
    Main loop that continuously captures screenshots and processes them.
    """
    last_opponent_move_time = time.time()

    while auto_mode_var.get():
        start_time = time.time()

        if processing_event.is_set():
            logger.debug("Currently processing a move; skipping frame.")
            time.sleep(screenshot_interval)
            continue

        screenshot = capture_screenshot_in_memory(root, auto_mode_var)
        if screenshot:
            frames.append(screenshot)

        # Analyze the latest frame for opponent's move
        if len(frames) > 0:
            latest_frame = frames[-1]
            boxes, midpoints, drag_offset = get_positions(latest_frame)
            if boxes:
                # Store the latest board positions, midpoints, and offset
                root.board_positions = midpoints
                root.drag_offset = drag_offset

                _, _, _, current_fen = get_fen_from_position(color_indicator, boxes)
                if current_fen:
                    placement, active_color = current_fen.split()[:2]

                    if active_color == opp_color:
                        if _handle_opponent_turn(opp_color, placement, last_fen_by_color):
                            last_opponent_move_time = time.time()

                    elif active_color == color_indicator:
                        move_detected = _handle_player_turn(opp_color, placement, last_fen_by_color)
                        if move_detected:
                            delay = _get_realistic_delay(last_opponent_move_time)
                            logger.info(f"Waiting for {delay:.2f} seconds before making a move.")
                            time.sleep(delay)
                            process_move(
                                root, color_indicator, auto_mode_var, board_positions,
                                update_status_callback,
                                update_last_fen_for_color, last_fen_by_color
                            )

        # Ensure the loop runs at the desired interval
        elapsed_time = time.time() - start_time
        sleep_time = max(0, screenshot_interval - elapsed_time)
        time.sleep(sleep_time)

def _get_realistic_delay(last_opponent_move_time):
    """
    Calculates a realistic delay based on the opponent's move time.
    """
    opponent_time = time.time() - last_opponent_move_time
    # Simple heuristic: delay is a fraction of opponent's time, with some randomness
    delay = opponent_time * random.uniform(0.5, 0.8) + random.uniform(0.2, 0.5)
    return max(0.5, min(delay, 5.0)) # Clamp between 0.5 and 5 seconds

def _handle_opponent_turn(opp_color, placement, last_fen_by_color):
    """
    Handle processing when it's the opponent's turn. Returns True if the opponent made a move.
    """
    old = last_fen_by_color.get(opp_color)
    if old is None or placement != old:
        logger.info("Opponent moved; updating last_fen_by_color[opp_color].")
        last_fen_by_color[opp_color] = placement
        return True
    else:
        logger.debug("Opponent placement unchanged.")
        return False

def _handle_player_turn(opp_color, placement, last_fen_by_color):
    """
    Handle processing when it's the player's turn.
    Returns True if a genuine opponent move was detected.
    """
    if opp_color not in last_fen_by_color or last_fen_by_color[opp_color] is None:
        logger.debug("Our turn, but no previous opponent FEN known; waiting for opponent move.")
        return False

    if placement != last_fen_by_color[opp_color]:
        logger.info("Detected genuine opponent move; launching our move.")
        last_fen_by_color[opp_color] = placement # Update with the new position
        return True

    return False

def _handle_loop_error(error, root, update_status_callback, auto_mode_var):
    """
    Handle errors that occur in the main processing loop.
    """
    logger.error(f"Exception in auto_move_loop: {error}", exc_info=True)
    root.after(0, lambda err=error: update_status_callback(f"Error: {str(err)}"))
    auto_mode_var.set(False)
