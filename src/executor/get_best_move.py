import os
import subprocess
import shutil
import logging
import sys
from utils.resource_path import resource_path

logger = logging.getLogger(__name__)
_stockfish_process = None

def get_root_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

CONFIG_FILE = os.path.join(get_root_dir(), "engine_config.txt")

def create_default_config(config_path):
    with open(config_path, "w") as f:
        f.write("# ChessPilot Engine Configuration\n")
        f.write("setoption name Hash value 1024\n")
        f.write("setoption name Threads value 4\n")
    logger.info(f"Created default config file at {config_path}")

def load_engine_config(stockfish_proc):
    if not os.path.exists(CONFIG_FILE):
        create_default_config(CONFIG_FILE)

    with open(CONFIG_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                stockfish_proc.stdin.write(f"{line}\n")
            except Exception as e:
                logger.warning(f"Failed to apply config line '{line}': {e}")

    stockfish_proc.stdin.write("isready\n")
    stockfish_proc.stdin.flush()
    while True:
        line = stockfish_proc.stdout.readline().strip()
        if line == "readyok":
            break

def _initialize_stockfish():
    global _stockfish_process
    if _stockfish_process:
        return _stockfish_process
    
    try:
        stockfish_path = resource_path("stockfish.exe" if os.name == "nt" else "stockfish")
        if not os.path.exists(stockfish_path):
             sys_stock = shutil.which("stockfish")
             if sys_stock:
                 stockfish_path = sys_stock
             else:
                raise FileNotFoundError("Stockfish not found.")

        command = stockfish_path if os.name == "nt" else [stockfish_path]
        _stockfish_process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        )
        load_engine_config(_stockfish_process)
        logger.info("Stockfish process initialized")
        return _stockfish_process
    except Exception as e:
        logger.error(f"Failed to initialize Stockfish: {e}", exc_info=True)
        _stockfish_process = None
        raise

def cleanup_stockfish():
    global _stockfish_process
    if _stockfish_process:
        try:
            _stockfish_process.stdin.write("quit\n")
            _stockfish_process.stdin.flush()
        except Exception:
            pass
        finally:
            _stockfish_process.terminate()
            _stockfish_process.wait()
            _stockfish_process = None
            logger.info("Stockfish process cleaned up")

def initialize_stockfish_at_startup():
    try:
        _initialize_stockfish()
        return True
    except Exception:
        return False

def get_best_move(depth, fen):
    try:
        stockfish = _initialize_stockfish()
        if not stockfish:
            raise Exception("Stockfish not initialized.")
        
        stockfish.stdin.write(f"position fen {fen}\n")
        stockfish.stdin.write(f"go depth {depth}\n")
        stockfish.stdin.flush()
        
        best_move = None
        mate_flag = False
        while True:
            line = stockfish.stdout.readline().strip()
            if not line:
                break
            if "bestmove" in line:
                best_move = line.split()[1]
                break
            if "score mate 1" in line or "score mate -1" in line:
                mate_flag = True
        
        if not best_move:
            return None, None, False

        stockfish.stdin.write(f"position fen {fen} moves {best_move}\n")
        stockfish.stdin.write("d\n")
        stockfish.stdin.flush()
        
        updated_fen = None
        while True:
            line = stockfish.stdout.readline().strip()
            if not line:
                break
            if "Fen:" in line:
                updated_fen = line.split("Fen:")[1].strip()
                break
        
        return best_move, updated_fen, mate_flag

    except Exception as e:
        logger.error(f"Stockfish error: {e}", exc_info=True)
        cleanup_stockfish()
        return None, None, False