import tkinter as tk
from tkinter import ttk
from .toggle_switch import create_toggle

class ModernTkinterApp(tk.Frame):
    def __init__(self, master=None, app_logic=None):
        super().__init__(master)
        self.master = master
        self.app = app_logic
        self.master.title("ChessPilot")
        self.master.geometry("400x600")
        self.master.resizable(False, False)
        self.master.attributes('-topmost', True)

        self.bg_color = "#2D2D2D"
        self.frame_color = "#373737"
        self.accent_color = "#4CAF50"
        self.text_color = "#FFFFFF"

        self.master.configure(bg=self.bg_color)

        self.create_styles()
        self.create_widgets()

    def create_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TScale", troughcolor=self.bg_color, background=self.accent_color)

    def create_widgets(self):
        main_frame = tk.Frame(self.master, bg=self.bg_color, padx=15, pady=15)
        main_frame.pack(expand=True, fill=tk.BOTH)

        header = tk.Label(main_frame, text="ChessPilot", font=('Segoe UI', 24, 'bold'), bg=self.bg_color, fg=self.accent_color)
        header.pack(pady=(0, 10))

        status_label = tk.Label(main_frame, textvariable=self.app.status_var, font=('Segoe UI', 10), bg=self.bg_color, fg=self.text_color, wraplength=350)
        status_label.pack(pady=5)
        best_move_label = tk.Label(main_frame, textvariable=self.app.best_move_var, font=('Segoe UI', 12, 'bold'), bg=self.bg_color, fg=self.accent_color)
        best_move_label.pack(pady=10)

        capture_play_frame = tk.Frame(main_frame, bg=self.bg_color)
        capture_play_frame.pack(fill=tk.X, pady=10)

        self.capture_button = tk.Button(capture_play_frame, text="▶", font=('Segoe UI', 20, 'bold'), bg="#373737", fg="#00FF00", relief=tk.FLAT, width=3, command=self.app.toggle_capture)
        self.capture_button.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.play_button = tk.Button(capture_play_frame, text="Play Next Move", font=('Segoe UI', 14, 'bold'), bg=self.accent_color, fg=self.text_color, relief=tk.FLAT, padx=10, command=self.app.play_best_move)
        self.play_button.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(10, 0))

        controls_frame = tk.Frame(main_frame, bg=self.frame_color, pady=10)
        controls_frame.pack(fill=tk.X, pady=10)

        # Toggles
        self.side_toggle = self.create_toggle_row(controls_frame, "Side:", self.app.flip_board, self.app.side_state_var)
        self.drag_click_toggle = self.create_toggle_row(controls_frame, "Mode:", self.app.toggle_drag_click, self.app.drag_click_state_var)
        self.autoplay_toggle = self.create_toggle_row(controls_frame, "Auto-Play:", self.app.toggle_auto_mode, self.app.autoplay_state_var)
        self.mute_toggle = self.create_toggle_row(controls_frame, "Sound:", self.app.toggle_mute, self.app.mute_state_var)

        # Sliders
        self.volume_slider = self.create_slider_row(controls_frame, "Volume:", self.app.set_volume, 0, 100)
        self.transparency_slider = self.create_slider_row(controls_frame, "Transparency:", self.app.set_transparency, 20, 100)
        self.volume_slider.set(10)
        self.transparency_slider.set(75)

        footer = tk.Label(main_frame, text="Made by Niladri | Powered by NiluAI", font=('Segoe UI', 8), bg=self.bg_color, fg="#AAAAAA")
        footer.pack(side=tk.BOTTOM, pady=(10, 0))

    def create_toggle_row(self, parent, label_text, command, state_var):
        row = tk.Frame(parent, bg=self.frame_color)
        row.pack(fill=tk.X, padx=10, pady=5)
        label = tk.Label(row, text=label_text, font=('Segoe UI', 10), bg=self.frame_color, fg=self.text_color)
        label.pack(side=tk.LEFT)

        state_label = tk.Label(row, textvariable=state_var, font=('Segoe UI', 10, 'bold'), bg=self.frame_color, fg=self.text_color)
        state_label.pack(side=tk.LEFT, padx=10)

        toggle = create_toggle(row, width=50, height=25, mode="dark", command=command)
        toggle.pack(side=tk.RIGHT)
        return toggle

    def create_slider_row(self, parent, label_text, command, from_, to):
        row = tk.Frame(parent, bg=self.frame_color)
        row.pack(fill=tk.X, padx=10, pady=5)
        label = tk.Label(row, text=label_text, font=('Segoe UI', 10), bg=self.frame_color, fg=self.text_color)
        label.pack(side=tk.LEFT)
        slider = ttk.Scale(row, from_=from_, to=to, orient="horizontal", command=command)
        slider.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        return slider
