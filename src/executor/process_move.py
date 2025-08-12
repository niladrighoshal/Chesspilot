import logging
from board_detection import get_positions, get_fen_from_position
from executor.capture_screenshot_in_memory import capture_screenshot_in_memory
from executor.store_board_positions import store_board_positions
from executor.get_best_move import get_best_move
from executor.execute_normal_move import execute_normal_move
from executor.processing_sync import processing_event

logger = logging.getLogger(__name__)

def process_move(app):
    if processing_event.is_set():
        logger.warning("Move already being processed.")
        return

    processing_event.set()
    app.update_status("Processing move...")
    logger.info("Processing move...")
    
    screenshot_image = capture_screenshot_in_memory()
    if not screenshot_image:
        app.update_status("Screenshot capture failed.")
        processing_event.clear()
        return

    boxes, midpoints, _ = get_positions(screenshot_image)
    if not boxes:
        app.update_status("No board detected.")
        processing_event.clear()
        return
    
    app.board_positions = midpoints
    store_board_positions(app.board_positions, boxes[0][0], boxes[0][1], boxes[0][2])
    _, _, _, fen = get_fen_from_position(app.color_indicator, boxes)
    
    if not fen:
        app.update_status("Could not detect FEN.")
        processing_event.clear()
        return

    move_data = get_best_move(22, fen)
    if not move_data or not move_data[0]:
        app.update_status("No valid move found.")
        processing_event.clear()
        return

    best_move, updated_fen, mate_flag = move_data
    
    app.last_fen_by_color[app.color_indicator] = updated_fen.split(' ')[0]
    
    execute_normal_move(app, best_move, updated_fen, mate_flag)

    processing_event.clear()
    if not app.auto_mode:
        app.gui.play_button.setDisabled(False)