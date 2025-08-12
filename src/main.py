import sys
import threading
import time
import logging
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from gui.pyqt_app import ChessPilotGUI
from utils.logging_setup import setup_console_logging
from utils.chess_resources_manager import setup_resources
from auto_mode import auto_move_loop
from executor import (
    capture_screenshot_in_memory,
    did_my_piece_move,
    get_best_move,
    cleanup_stockfish,
    initialize_stockfish_at_startup,
    get_current_fen,
    process_move,
    execute_normal_move
)
from board_detection import get_positions, get_fen_from_position
from board_detection.side_detector import detect_side_from_fen
from utils.speech import speak, get_piece_name

# --- Worker for background tasks ---
class Worker(QObject):
    status_update = pyqtSignal(str)
    best_move_update = pyqtSignal(str)
    side_detected = pyqtSignal(str)
    board_detected = pyqtSignal(bool)

    def __init__(self, app_logic):
        super().__init__()
        self.app = app_logic
        self.is_running = True

    def stop(self):
        self.is_running = False

    def run_board_detection_loop(self):
        while self.is_running:
            if not self.app.is_capturing:
                time.sleep(0.5)
                continue

            self.status_update.emit("Scanning for board...")
            screenshot = capture_screenshot_in_memory()
            if screenshot:
                boxes, midpoints, drag_offset = get_positions(screenshot)
                if boxes:
                    if len(boxes) > 32:
                        self.status_update.emit("Multiple boards detected! Pausing capture.")
                        self.board_detected.emit(False)
                        self.app.is_capturing = False
                    else:
                        self.status_update.emit("Board detected.")
                        self.app.board_positions = midpoints
                else:
                    self.status_update.emit("No board detected.")
            time.sleep(1)

    def run_auto_side_detection(self):
        self.status_update.emit("Attempting to auto-detect side...")
        fen = self.app.read_current_fen_once()
        if fen:
            side = detect_side_from_fen(fen)
            self.side_detected.emit(side)
        else:
            self.status_update.emit("Could not detect FEN for side detection.")

# --- Main Application Logic ---
class ChessPilot(QObject):
    def __init__(self, gui):
        super().__init__()
        self.gui = gui
        self.is_closing = False
        self.is_capturing = False
        
        self.color_indicator = None
        self.auto_mode = False
        self.drag_mode = True
        self.board_positions = {}
        self.last_fen_by_color = {'w': None, 'b': None}

        self.setup_connections()

        self.worker = Worker(self)
        self.thread = threading.Thread(target=self.worker.run_board_detection_loop)
        self.thread.daemon = True
        self.thread.start()

    def setup_connections(self):
        self.gui.play_button.clicked.connect(self.process_move_thread)
        self.gui.capture_toggle.toggled.connect(self.toggle_capture)
        self.gui.autoplay_toggle.toggled.connect(self.toggle_auto_mode)
        self.gui.side_toggle.toggled.connect(self.flip_board)
        self.gui.drag_click_toggle.toggled.connect(self.toggle_drag_click)
        self.gui.transparency_slider.valueChanged.connect(self.set_transparency)
        self.gui.destroyed.connect(self.on_closing)

        self.worker.status_update.connect(self.update_status)
        self.worker.best_move_update.connect(self.update_best_move)
        self.worker.side_detected.connect(self.on_side_detected)
        self.worker.board_detected.connect(self.on_board_detected)

    @pyqtSlot(str)
    def update_status(self, message):
        self.gui.status_label.setText(message)

    @pyqtSlot(str)
    def update_best_move(self, move_text):
        self.gui.best_move_label.setText(move_text)

    @pyqtSlot(str)
    def on_side_detected(self, side):
        self.color_indicator = side
        self.gui.side_toggle.setChecked(side == 'b')
        self.update_status(f"Auto-detected side: {'White' if side == 'w' else 'Black'}")

    @pyqtSlot(bool)
    def on_board_detected(self, detected):
        self.gui.capture_toggle.setChecked(detected)

    def toggle_capture(self, checked):
        self.is_capturing = checked
        if checked and self.color_indicator is None:
             threading.Thread(target=self.worker.run_auto_side_detection).start()

    def toggle_auto_mode(self, checked):
        self.auto_mode = checked
        self.gui.play_button.setDisabled(checked)
        if checked:
            threading.Thread(target=auto_move_loop, args=(self,), daemon=True).start()

    def toggle_drag_click(self, checked):
        self.drag_mode = not checked

    def flip_board(self, checked):
        self.color_indicator = 'b' if checked else 'w'
        self.update_status(f"Side set to {'Black' if self.color_indicator == 'b' else 'White'}")

    def set_transparency(self, value):
        self.gui.setWindowOpacity(value / 100.0)

    def process_move_thread(self):
        if self.is_capturing:
            threading.Thread(target=process_move, args=(self,), daemon=True).start()
        else:
            self.update_status("Please enable screen capture first.")

    def read_current_fen_once(self):
        screenshot = capture_screenshot_in_memory()
        if screenshot:
            boxes, _, _ = get_positions(screenshot)
            if boxes:
                _, _, _, fen = get_fen_from_position('w', boxes)
                return fen
        return None

    def on_closing(self):
        self.is_closing = True
        self.worker.stop()
        cleanup_stockfish()
        logger.info("Application closing.")

def main():
    setup_console_logging()
    if not setup_resources(os.path.dirname(__file__), os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))):
        logger.error("Resource setup failed.")
        return -1

    if not initialize_stockfish_at_startup():
        logger.warning("Stockfish initialization failed.")

    app = QApplication(sys.argv)
    gui = ChessPilotGUI()
    logic = ChessPilot(gui)
    gui.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
