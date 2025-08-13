import mss
from PIL import Image
import io
from .is_wayland import is_wayland
import subprocess
from tkinter import messagebox
import logging
from utils.get_binary_path import get_binary_path

logger = logging.getLogger(__name__)

def capture_screenshot_in_memory(app=None):
    grim_path = get_binary_path("grim") if is_wayland() else None
    try:
        if is_wayland():
            logger.info("Capturing screenshot using grim (Wayland)...")
            result = subprocess.run([grim_path, "-"], stdout=subprocess.PIPE, check=True)
            image = Image.open(io.BytesIO(result.stdout))
        else:
            logger.info("Capturing screenshot using mss (non-Wayland)...")
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                sct_img = sct.grab(monitor)
                image = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
        logger.debug("Screenshot captured successfully")
        return image
    except Exception as e:
        logger.error(f"Screenshot failed: {e}")
        if app and hasattr(app, 'gui'):
            app.gui.master.after(0, lambda err=e: messagebox.showerror("Error", f"Screenshot failed: {str(err)}"))
        if app and hasattr(app, 'auto_mode'):
            app.auto_mode = False
            if hasattr(app, 'gui'):
                app.gui.autoplay_var.set(False)
        return None
