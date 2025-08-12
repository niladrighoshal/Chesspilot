import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSlider, QFrame
from PyQt5.QtGui import QIcon, QFont, QColor
from PyQt5.QtCore import Qt, QSize
from qtwidgets import AnimatedToggle

class ChessPilotGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChessPilot")
        self.setGeometry(100, 100, 400, 600)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setAlignment(Qt.AlignTop)

        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #2D2D2D;
                color: #FFFFFF;
                font-family: 'Segoe UI';
            }
            QFrame#controls_frame {
                background-color: #373737;
                border-radius: 10px;
                padding: 10px;
            }
            QLabel {
                font-size: 10pt;
            }
            QPushButton#play_button {
                font-size: 16pt;
                font-weight: bold;
                background-color: #4CAF50;
                color: white;
                padding: 12px;
                border-radius: 8px;
            }
            QPushButton#play_button:hover {
                background-color: #45a049;
            }
            QPushButton#capture_toggle {
                border: none;
            }
        """)

    def create_widgets(self):
        # Header
        header = QLabel("ChessPilot")
        header.setFont(QFont("Segoe UI", 24, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: #4CAF50;")
        self.layout.addWidget(header)

        # Status & Best Move
        self.status_label = QLabel("Initializing...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.status_label)

        self.best_move_label = QLabel("Best Move: ...")
        self.best_move_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.best_move_label.setAlignment(Qt.AlignCenter)
        self.best_move_label.setStyleSheet("color: #4CAF50;")
        self.layout.addWidget(self.best_move_label)

        # Spacer
        self.layout.addSpacing(20)

        # Capture Toggle
        self.capture_toggle = QPushButton()
        self.capture_toggle.setObjectName("capture_toggle")
        self.capture_toggle.setCheckable(True)
        self.capture_toggle.setIcon(self.style().standardIcon(QApplication.SP_DialogCancelButton))
        self.capture_toggle.setIconSize(QSize(48, 48))
        self.capture_toggle.toggled.connect(self.on_capture_toggled)
        self.layout.addWidget(self.create_labeled_widget("Capture Screen (Enter)", self.capture_toggle, alignment=Qt.AlignCenter))

        # Play Button
        self.play_button = QPushButton("Play Next Move")
        self.play_button.setObjectName("play_button")
        self.layout.addWidget(self.create_labeled_widget("(Space)", self.play_button, alignment=Qt.AlignCenter))

        # Controls Frame
        controls_frame = QFrame()
        controls_frame.setObjectName("controls_frame")
        controls_layout = QVBoxLayout(controls_frame)
        self.layout.addWidget(controls_frame)

        # Toggles
        self.side_toggle = AnimatedToggle(checked_color="#E0E0E0", unchecked_color="#505050")
        self.autoplay_toggle = AnimatedToggle(checked_color="#4CAF50")
        self.drag_click_toggle = AnimatedToggle(checked_color="#0E80C0")
        self.mute_toggle = AnimatedToggle(checked_color="#FFB000")

        controls_layout.addWidget(self.create_labeled_widget("Side (W/B):", self.side_toggle, "W / B"))
        controls_layout.addWidget(self.create_labeled_widget("Auto Play (A):", self.autoplay_toggle))
        controls_layout.addWidget(self.create_labeled_widget("Drag/Click (Ctrl):", self.drag_click_toggle, "Drag / Click"))
        controls_layout.addWidget(self.create_labeled_widget("Mute (M):", self.mute_toggle))

        # Sliders
        self.volume_slider = self.create_slider_row("Volume (Up/Down):", controls_layout)
        self.transparency_slider = self.create_slider_row("Transparency (Left/Right):", controls_layout, 20, 100)
        self.transparency_slider.setValue(100)

        # Footer
        self.layout.addStretch()
        footer = QLabel("Made by Niladri | Powered by NiluAI")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #AAAAAA; font-size: 8pt;")
        self.layout.addWidget(footer)

    def create_labeled_widget(self, label_text, widget, keybind_hint=None, alignment=Qt.AlignRight):
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(label_text)
        row_layout.addWidget(label)

        row_layout.addStretch()

        if keybind_hint:
            hint_label = QLabel(keybind_hint)
            hint_label.setStyleSheet("color: #888888; font-size: 8pt;")
            row_layout.addWidget(hint_label)
            row_layout.addSpacing(10)

        row_layout.addWidget(widget, alignment=alignment)
        return row

    def create_slider_row(self, label_text, parent_layout, min_val, max_val):
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_val, max_val)
        parent_layout.addWidget(self.create_labeled_widget(label_text, slider))
        return slider

    def on_capture_toggled(self, checked):
        if checked:
            self.capture_toggle.setIcon(self.style().standardIcon(QApplication.SP_DialogApplyButton))
        else:
            self.capture_toggle.setIcon(self.style().standardIcon(QApplication.SP_DialogCancelButton))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = ChessPilotGUI()
    win.show()
    sys.exit(app.exec_())
