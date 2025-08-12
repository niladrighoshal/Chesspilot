import tkinter as tk
import logging

# Logger setup
logger = logging.getLogger(__name__)

def handle_esc_key(app, event=None):
    """Return to color‐selection screen if ESC is pressed."""
    logger.info("ESC key pressed; returning to color selection")
    if app.main_frame.winfo_ismapped():
        app.main_frame.pack_forget()
        app.color_frame.pack(expand=True, fill=tk.BOTH)
        app.color_indicator = None
        app.btn_play.config(state=tk.DISABLED)
        app.update_status("")
        app.auto_mode_var.set(False)
        app.btn_play.config(state=tk.NORMAL)
        
def bind_shortcuts(app):
    """Bind keyboard shortcuts to various actions."""
    # Color selection shortcuts
    app.root.bind('<Key-w>', lambda e: app.set_color('w'))
    app.root.bind('<Key-b>', lambda e: app.set_color('b'))

    # Main control shortcuts
    app.root.bind('<space>', lambda e: app.process_move_thread() if app.color_indicator else None)
    app.root.bind('<Key-m>', lambda e: app.speech_mute_var.set(not app.speech_mute_var.get()))

    # Volume control
    app.root.bind('<Up>', lambda e: app.speech_volume_var.set(min(1.0, app.speech_volume_var.get() + 0.1)))
    app.root.bind('<Down>', lambda e: app.speech_volume_var.set(max(0.0, app.speech_volume_var.get() - 0.1)))

    # Transparency control
    app.root.bind('<Right>', lambda e: app.transparency_var.set(min(1.0, app.transparency_var.get() + 0.1)))
    app.root.bind('<Left>', lambda e: app.transparency_var.set(max(0.2, app.transparency_var.get() - 0.1)))
