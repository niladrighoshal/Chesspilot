import tkinter as tk
from tkinter import ttk
import logging

logger = logging.getLogger(__name__)

class ChessPilotGUI(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("ChessPilot")
        self.master.geometry("400x500")
        self.master.resizable(False, False)
        self.master.attributes('-topmost', True)

        self.bg_color = "#2D2D2D"
        self.frame_color = "#373737"
        self.accent_color = "#4CAF50"
        self.text_color = "#FFFFFF"

        self.master.configure(bg=self.bg_color)

        self.create_widgets()

    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.master, bg=self.bg_color)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Header
        header = tk.Label(main_frame, text="ChessPilot", font=('Segoe UI', 22, 'bold'), bg=self.bg_color, fg=self.accent_color)
        header.pack(pady=(10, 20))

        # Status Label
        self.status_var = tk.StringVar(value="Initializing...")
        status_label = tk.Label(main_frame, textvariable=self.status_var, font=('Segoe UI', 10), bg=self.bg_color, fg=self.text_color)
        status_label.pack(pady=10)

        # Best Move Label
        self.best_move_var = tk.StringVar(value="Best Move: ...")
        best_move_label = tk.Label(main_frame, textvariable=self.best_move_var, font=('Segoe UI', 12, 'bold'), bg=self.bg_color, fg=self.accent_color)
        best_move_label.pack(pady=10)

        # Play Button
        self.play_button = tk.Button(main_frame, text="Play Next Move", font=('Segoe UI', 16, 'bold'), bg=self.accent_color, fg=self.text_color, relief=tk.FLAT, padx=20, pady=10)
        self.play_button.pack(fill=tk.X, pady=10, ipady=10)

        # Controls Frame
        controls_frame = tk.Frame(main_frame, bg=self.frame_color)
        controls_frame.pack(fill=tk.X, pady=10)

        # Side Toggle
        self.side_var = tk.StringVar(value="w")
        side_frame = tk.Frame(controls_frame, bg=self.frame_color)
        tk.Label(side_frame, text="Side:", font=('Segoe UI', 10), bg=self.frame_color, fg=self.text_color).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(side_frame, text="White", variable=self.side_var, value="w").pack(side=tk.LEFT)
        ttk.Radiobutton(side_frame, text="Black", variable=self.side_var, value="b").pack(side=tk.LEFT)
        side_frame.pack(pady=5)

        # Execution Mode
        self.execution_mode_var = tk.StringVar(value="drag")
        execution_frame = tk.Frame(controls_frame, bg=self.frame_color)
        tk.Label(execution_frame, text="Move Execution:", bg=self.frame_color, fg=self.text_color).pack(side="left", padx=5)
        ttk.Radiobutton(execution_frame, text="Drag", variable=self.execution_mode_var, value="drag").pack(side="left")
        ttk.Radiobutton(execution_frame, text="Click", variable=self.execution_mode_var, value="click").pack(side="left")
        execution_frame.pack(pady=5)

        # Auto Play Toggle
        self.autoplay_var = tk.BooleanVar(value=False)
        self.autoplay_check = ttk.Checkbutton(controls_frame, text="Auto Play", variable=self.autoplay_var)
        self.autoplay_check.pack(pady=5)

        # Flip Button
        self.flip_button = tk.Button(controls_frame, text="Flip Side", font=('Segoe UI', 10), bg=self.accent_color, fg=self.text_color, relief=tk.FLAT)
        self.flip_button.pack(fill=tk.X, pady=5)

        # Sliders
        self.volume_var = tk.DoubleVar(value=0.5)
        volume_frame = tk.Frame(controls_frame, bg=self.frame_color)
        tk.Label(volume_frame, text="Volume:", font=('Segoe UI', 10), bg=self.frame_color, fg=self.text_color).pack(side=tk.LEFT, padx=5)
        self.volume_slider = ttk.Scale(volume_frame, from_=0.0, to=1.0, variable=self.volume_var)
        self.volume_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.mute_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(volume_frame, text="Mute", variable=self.mute_var).pack(side=tk.LEFT, padx=5)
        volume_frame.pack(fill=tk.X, pady=5)

        self.transparency_var = tk.DoubleVar(value=1.0)
        transparency_frame = tk.Frame(controls_frame, bg=self.frame_color)
        tk.Label(transparency_frame, text="Transparency:", font=('Segoe UI', 10), bg=self.frame_color, fg=self.text_color).pack(side=tk.LEFT, padx=5)
        self.transparency_slider = ttk.Scale(transparency_frame, from_=0.2, to=1.0, variable=self.transparency_var, command=self.master.set_transparency)
        self.transparency_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        transparency_frame.pack(fill=tk.X, pady=5)

        # Footer
        footer = tk.Frame(self.master, bg=self.bg_color)
        footer.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        tk.Label(footer, text="Made by Niladri", font=('Segoe UI', 8), bg=self.bg_color, fg=self.text_color).pack(side=tk.LEFT, padx=10)
        tk.Label(footer, text="Powered by NiluAI", font=('Segoe UI', 8), bg=self.bg_color, fg=self.text_color).pack(side=tk.RIGHT, padx=10)

if __name__ == '__main__':
    root = tk.Tk()
    app = ChessPilotGUI(master=root)
    app.mainloop()
