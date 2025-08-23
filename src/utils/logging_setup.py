import logging

class ColorFormatter(logging.Formatter):
    LEVEL_COLORS = {
        logging.DEBUG: "\x1b[36m",  # Cyan
        logging.INFO: "\x1b[32m",   # Green
        logging.WARNING: "\x1b[33m",# Yellow
        logging.ERROR: "\x1b[31m",  # Red
        logging.CRITICAL: "\x1b[31;1m",# Bold Red
    }
    COLOR_RESET = "\x1b[0m"

    def format(self, record):
        color = self.LEVEL_COLORS.get(record.levelno, "")
        record.levelname = f"{color}{record.levelname:<8}{self.COLOR_RESET}"
        record.msg = f"{color}{record.msg}{self.COLOR_RESET}"
        return super().format(record)

def setup_console_logging(level=logging.INFO):
    # Set comtypes logger to INFO to avoid spam
    logging.getLogger('comtypes').setLevel(logging.INFO)

    root_logger = logging.getLogger()
    # Avoid adding handlers multiple times
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    root_logger.setLevel(level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # New format with milliseconds
    fmt = "[%(asctime)s.%(msecs)03d] [%(levelname)s] %(message)s"
    datefmt = "%H:%M:%S"

    # Use color formatter only if the stream supports it
    if hasattr(console_handler.stream, 'isatty') and console_handler.stream.isatty():
        formatter = ColorFormatter(fmt, datefmt=datefmt)
    else:
        formatter = logging.Formatter(fmt, datefmt=datefmt)

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)