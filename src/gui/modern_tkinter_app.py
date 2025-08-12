import tkinter as tk
from tkinter import ttk

class ModernTkinterApp(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("ChessPilot")
        self.master.geometry("400x600")
        self.master.resizable(False, False)
        self.master.attributes('-topmost', True)

        self.bg_color = "#2D2D2D"
        self.frame_color = "#373737"
        self.accent_color = "#4CAF50"
        self.text_color = "#FFFFFF"

        self.master.configure(bg=self.bg_color)

        self.create_variables()
        self.create_styles()
        self.create_widgets()

    def create_variables(self):
        self.status_var = tk.StringVar(value="Initializing...")
        self.best_move_var = tk.StringVar(value="Best Move: ...")
        self.capture_var = tk.BooleanVar(value=False)
        self.side_var = tk.StringVar(value="w")
        self.autoplay_var = tk.BooleanVar(value=False)
        self.drag_click_var = tk.StringVar(value="drag")
        self.mute_var = tk.BooleanVar(value=False)
        self.volume_var = tk.DoubleVar(value=50)
        self.transparency_var = tk.DoubleVar(value=100)

    def create_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TCheckbutton", background=self.frame_color, foreground=self.text_color, font=('Segoe UI', 10))
        style.configure("TRadiobutton", background=self.frame_color, foreground=self.text_color, font=('Segoe UI', 10))
        style.configure("TScale", troughcolor=self.bg_color, background=self.accent_color)

    def create_widgets(self):
        main_frame = tk.Frame(self.master, bg=self.bg_color, padx=15, pady=15)
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Header
        header = tk.Label(main_frame, text="ChessPilot", font=('Segoe UI', 24, 'bold'), bg=self.bg_color, fg=self.accent_color)
        header.pack(pady=(0, 10))

        # Status & Best Move
        status_label = tk.Label(main_frame, textvariable=self.status_var, font=('Segoe UI', 10), bg=self.bg_color, fg=self.text_color, wraplength=350)
        status_label.pack(pady=5)
        best_move_label = tk.Label(main_frame, textvariable=self.best_move_var, font=('Segoe UI', 12, 'bold'), bg=self.bg_color, fg=self.accent_color)
        best_move_label.pack(pady=10)

        # --- Capture and Play ---
        capture_play_frame = tk.Frame(main_frame, bg=self.bg_color)
        capture_play_frame.pack(fill=tk.X, pady=10)

        self.capture_button = tk.Button(capture_play_frame, text="▶", font=('Segoe UI', 20, 'bold'), bg="#373737", fg="#00FF00", relief=tk.FLAT, width=3)
        self.capture_button.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.play_button = tk.Button(capture_play_frame, text="Play Next Move", font=('Segoe UI', 14, 'bold'), bg=self.accent_color, fg=self.text_color, relief=tk.FLAT, padx=10)
        self.play_button.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(10, 0))

        # --- Controls Frame ---
        controls_frame = tk.Frame(main_frame, bg=self.frame_color, pady=10)
        controls_frame.pack(fill=tk.X, pady=10)

        # Toggles
        self.create_check_row(controls_frame, "Auto Play (A)", self.autoplay_var)
        self.create_check_row(controls_frame, "Mute (M)", self.mute_var)
        self.create_check_row(controls_frame, "Side (W/B)", self.side_var, onvalue='b', offvalue='w')
        self.create_check_row(controls_frame, "Drag/Click (Ctrl)", self.drag_click_var, onvalue='click', offvalue='drag')

        # Sliders
        self.create_slider_row(controls_frame, "Volume (Up/Down)", self.volume_var, 0, 100)
        self.create_slider_row(controls_frame, "Transparency (Left/Right)", self.transparency_var, 20, 100)

        # Footer
        footer = tk.Label(main_frame, text="Made by Niladri | Powered by NiluAI", font=('Segoe UI', 8), bg=self.bg_color, fg="#AAAAAA")
        footer.pack(side=tk.BOTTOM, pady=(10, 0))

    def create_check_row(self, parent, label_text, variable, onvalue=True, offvalue=False):
        row = tk.Frame(parent, bg=self.frame_color)
        row.pack(fill=tk.X, padx=10, pady=2)
        label = tk.Label(row, text=label_text, font=('Segoe UI', 10), bg=self.frame_color, fg=self.text_color)
        label.pack(side=tk.LEFT)
        check = ttk.Checkbutton(row, variable=variable, onvalue=onvalue, offvalue=offvalue)
        check.pack(side=tk.RIGHT)
        return check

    def create_slider_row(self, parent, label_text, variable, from_, to):
        row = tk.Frame(parent, bg=self.frame_color)
        row.pack(fill=tk.X, padx=10, pady=5)
        label = tk.Label(row, text=label_text, font=('Segoe UI', 10), bg=self.frame_color, fg=self.text_color)
        label.pack(side=tk.LEFT)
        slider = ttk.Scale(row, from_=from_, to=to, orient="horizontal", variable=variable)
        slider.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        return slider

if __name__ == '__main__':
    root = tk.Tk()
    app = ModernTkinterApp(master=root)
    app.mainloop()
