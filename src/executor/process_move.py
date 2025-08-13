import logging
from executor.execute_normal_move import execute_normal_move
from executor.get_current_fen import get_current_fen
from executor.processing_sync import processing_event

logger = logging.getLogger(__name__)

def process_move(app, move):
    if processing_event.is_set():
        logger.warning("Move already being processed.")
        return

    processing_event.set()
    app.update_status(f"Playing move: {move}...")

    try:
        fen = get_current_fen(app.color_indicator)
        if not fen:
            app.update_status("Could not get current FEN.")
            processing_event.clear()
            return

        execute_normal_move(app, move, None, False)
        app.move_count += 1

    except Exception as e:
        logger.error(f"Error during move processing: {e}", exc_info=True)
        app.update_status(f"Error: {e}")
    finally:
        processing_event.clear()
        if not app.auto_mode:
            app.gui.play_button.setDisabled(False)