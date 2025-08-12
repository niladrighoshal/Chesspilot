import os
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

def resource_path(relative_path: str) -> str:
    """
    Get the absolute path to a resource, works for dev and for PyInstaller.
    It now checks environment variables first, which are set by chess_resources_manager.
    """
    # Check environment variables first
    if "stockfish" in relative_path.lower():
        env_path = os.environ.get("STOCKFISH_PATH")
        if env_path:
            logger.debug(f"Using STOCKFISH_PATH from environment: {env_path}")
            return env_path

    if "chess_detection.onnx" in relative_path:
        env_path = os.environ.get("ONNX_PATH")
        if env_path:
            logger.debug(f"Using ONNX_PATH from environment: {env_path}")
            return env_path

    # PyInstaller creates a temp folder and stores path in _MEIPASS
    if getattr(sys, 'frozen', False):
        base_path = Path(sys._MEIPASS)
    else:
        # In development, resources are in the 'src' directory
        base_path = Path(__file__).parent.parent

    resolved_path = base_path / relative_path
    logger.debug(f"Resolved resource path for '{relative_path}': {resolved_path}")
    return str(resolved_path)
