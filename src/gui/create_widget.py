import tkinter as tk
from tkinter import ttk
import logging

# Logger setup
logger = logging.getLogger(__name__)

def create_widgets(app):
    # Color selection screen
    logger.debug("Creating color selection widgets")
    app.color_frame = tk.Frame(app.root, bg=app.bg_color)
    header = tk.Label(
        app.color_frame,
        text="ChessPilot",
        font=('Segoe UI', 18, 'bold'),
        bg=app.bg_color,
        fg=app.accent_color
    )
    header.pack(pady=(20, 10))

    color_panel = tk.Frame(app.color_frame, bg=app.frame_color, padx=20, pady=15)
    tk.Label(
        color_panel,
        text="Select Your Color:",
        font=('Segoe UI', 11),
        bg=app.frame_color,
        fg=app.text_color
    ).pack(pady=5)

    btn_frame = tk.Frame(color_panel, bg=app.frame_color)
    app.btn_white = app.create_color_button(btn_frame, "White", "w")
    app.btn_black = app.create_color_button(btn_frame, "Black", "b")
    btn_frame.pack(pady=5)

    # Depth and delay settings
    depth_panel = tk.Frame(color_panel, bg=app.frame_color)
    tk.Label(
        depth_panel,
        text="Auto Move Screenshot Delay (sec):",
        font=('Segoe UI', 10),
        bg=app.frame_color,
        fg=app.text_color
    ).pack(anchor='w')

    app.delay_spinbox = ttk.Spinbox(
        depth_panel,
        from_=0.0,
        to=1.0,
        increment=0.1,
        textvariable=app.screenshot_delay_var,
        format="%.1f",
        width=5,
        state="readonly",
        justify="center"
    )
    app.style.configure(
        "TSpinbox",
        fieldbackground="#F3F1F1",
        background=app.frame_color,
        foreground="#000000"
    )
    app.delay_spinbox.pack(anchor='w')

    depth_panel.pack(fill='x', pady=10)
    color_panel.pack(padx=30, pady=10, fill='x')
    app.color_frame.pack(expand=True, fill=tk.BOTH)

    # Main control screen (after color is chosen)
    logger.debug("Creating main control widgets")
    app.main_frame = tk.Frame(app.root, bg=app.bg_color)
    control_panel = tk.Frame(app.main_frame, bg=app.frame_color, padx=20, pady=15)

    app.best_move_label = tk.Label(
        control_panel,
        textvariable=app.best_move_var,
        font=('Segoe UI', 12, 'bold'),
        bg=app.frame_color,
        fg=app.accent_color,
    )
    app.best_move_label.pack(pady=10)

    app.btn_play = app.create_action_button(
        control_panel,
        "Play Next Move",
        app.process_move_thread
    )
    app.btn_play.config(font=('Segoe UI', 14, 'bold'))
    app.btn_play.pack(fill='x', pady=5, ipady=10)

    app.castling_frame = tk.Frame(control_panel, bg=app.frame_color)
    app.kingside_var = tk.BooleanVar()
    app.queenside_var = tk.BooleanVar()
    app.create_castling_checkboxes()
    app.castling_frame.pack(pady=10)

    app.auto_mode_check = ttk.Checkbutton(
        control_panel,
        text="Auto Next Moves",
        variable=app.auto_mode_var,
        command=app.toggle_auto_mode,
        style="Castling.TCheckbutton"
    )
    app.auto_mode_check.pack(pady=5, anchor="center")

    app.btn_flip = app.create_action_button(
        control_panel,
        "Flip Side",
        app.flip_board
    )
    app.btn_flip.pack(fill='x', pady=5)

    # Execution mode
    app.execution_mode_var = tk.StringVar(value="drag")
    execution_frame = tk.Frame(control_panel, bg=app.frame_color)
    tk.Label(execution_frame, text="Move Execution:", bg=app.frame_color, fg=app.text_color).pack(side="left", padx=5)
    ttk.Radiobutton(execution_frame, text="Drag", variable=app.execution_mode_var, value="drag").pack(side="left")
    ttk.Radiobutton(execution_frame, text="Click", variable=app.execution_mode_var, value="click").pack(side="left")
    execution_frame.pack(pady=5)

    # Speech controls
    speech_frame = tk.Frame(control_panel, bg=app.frame_color)
    tk.Label(speech_frame, text="Speech Volume:", bg=app.frame_color, fg=app.text_color).pack(side="left", padx=5)
    ttk.Scale(speech_frame, from_=0.0, to=1.0, variable=app.speech_volume_var).pack(side="left")
    ttk.Checkbutton(speech_frame, text="Mute", variable=app.speech_mute_var).pack(side="left", padx=5)
    speech_frame.pack(pady=5)

    # Transparency control
    transparency_frame = tk.Frame(control_panel, bg=app.frame_color)
    tk.Label(transparency_frame, text="Transparency:", bg=app.frame_color, fg=app.text_color).pack(side="left", padx=5)
    ttk.Scale(transparency_frame, from_=0.2, to=1.0, variable=app.transparency_var, command=app.set_transparency).pack(side="left")
    transparency_frame.pack(pady=5)

    app.status_label = tk.Label(
        control_panel,
        text="",
        font=('Segoe UI', 10),
        bg=app.frame_color,
        fg=app.text_color,
        wraplength=300
    )
    app.status_label.pack(fill='x', pady=10)

    control_panel.pack(padx=30, pady=20, fill='both', expand=True)
    app.main_frame.pack(expand=True, fill=tk.BOTH)

    # Disable "Play Next Move" until a color is chosen
    app.btn_play.config(state=tk.DISABLED)
    logger.debug("Widgets created successfully")
