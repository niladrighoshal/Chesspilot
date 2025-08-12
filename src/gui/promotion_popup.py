import tkinter as tk
from tkinter import ttk
import logging

logger = logging.getLogger(__name__)

class PromotionPopup(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Pawn Promotion")
        self.geometry("200x100")
        self.resizable(False, False)
        self.attributes('-topmost', True)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.selected_piece = None

        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        label = tk.Label(main_frame, text="Promote to:")
        label.pack(pady=5)

        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=5)

        ttk.Button(button_frame, text="Queen", command=lambda: self.select_piece("q")).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Rook", command=lambda: self.select_piece("r")).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Bishop", command=lambda: self.select_piece("b")).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Knight", command=lambda: self.select_piece("n")).pack(side=tk.LEFT, padx=5)

    def select_piece(self, piece):
        self.selected_piece = piece
        self.destroy()

    def on_closing(self):
        self.selected_piece = "q" # Default to queen if the window is closed
        self.destroy()

    def wait_for_selection(self):
        self.wait_window(self)
        return self.selected_piece

if __name__ == '__main__':
    root = tk.Tk()
    def open_popup():
        popup = PromotionPopup(master=root)
        piece = popup.wait_for_selection()
        print(f"Selected piece: {piece}")

    button = tk.Button(root, text="Open Promotion Popup", command=open_popup)
    button.pack(pady=20)
    root.mainloop()
