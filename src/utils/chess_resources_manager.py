import os
import zipfile
from pathlib import Path
import shutil
import logging
from shutil import which
import sys

logger = logging.getLogger(__name__)

def find_stockfish_executable(script_dir: Path) -> str:
    """Finds the stockfish executable."""
    stockfish_name = "stockfish.exe" if os.name == "nt" else "stockfish"

    # 1. Check in the script directory (src)
    local_path = script_dir / stockfish_name
    if local_path.exists():
        logger.info(f"Found Stockfish at {local_path}")
        return str(local_path)

    # 2. Check in system PATH
    system_path = which(stockfish_name)
    if system_path:
        logger.info(f"Found system-installed Stockfish at {system_path}")
        return system_path

    # 3. Check for a zip file in the project root (one level up from src)
    project_dir = script_dir.parent
    zip_path = project_dir / "stockfish.zip"
    if zip_path.exists():
        logger.info(f"Found stockfish.zip at {zip_path}, attempting to extract.")
        extract_to = script_dir
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            for member in zip_ref.infolist():
                if stockfish_name in member.filename:
                    zip_ref.extract(member, extract_to)
                    extracted_file = extract_to / member.filename
                    # Move to script_dir root if it's in a subdirectory
                    if extracted_file.parent != extract_to:
                        shutil.move(str(extracted_file), str(extract_to / extracted_file.name))
                    final_path = extract_to / stockfish_name
                    if not final_path.exists():
                         (extract_to / extracted_file.name).rename(final_path)
                    logger.info(f"Extracted Stockfish to {final_path}")
                    return str(final_path)

    logger.error("Stockfish executable not found in src/, system PATH, or as stockfish.zip in the project root.")
    return None

def find_onnx_model(script_dir: Path) -> str:
    """Finds the ONNX model."""
    onnx_name = "chess_detection.onnx"
    local_path = script_dir / onnx_name
    if local_path.exists():
        logger.info(f"Found ONNX model at {local_path}")
        return str(local_path)

    project_dir = script_dir.parent
    root_path = project_dir / onnx_name
    if root_path.exists():
        shutil.move(str(root_path), str(local_path))
        logger.info(f"Moved ONNX model from {root_path} to {local_path}")
        return str(local_path)

    logger.error(f"ONNX model '{onnx_name}' not found in src/ or project root.")
    return None

def setup_resources(script_dir_str: str, project_dir_str: str) -> bool:
    """
    Ensures that Stockfish and ONNX model are available.
    Looks for stockfish.exe in src/, system PATH, or extracts from stockfish.zip in project root.
    Looks for chess_detection.onnx in src/ or project root.
    """
    script_dir = Path(script_dir_str)

    stockfish_path = find_stockfish_executable(script_dir)
    onnx_path = find_onnx_model(script_dir)

    if stockfish_path and onnx_path:
        # This is a bit of a hack to make the resource_path function work later
        # We store the paths so they can be retrieved by other parts of the app
        os.environ["STOCKFISH_PATH"] = stockfish_path
        os.environ["ONNX_PATH"] = onnx_path
        return True

    return False
