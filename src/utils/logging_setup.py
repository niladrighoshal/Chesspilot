import logging

class RepeatFilter(logging.Filter):
    def __init__(self):
        super().__init__()
        self.last_log = None
        self.count = 0

    def filter(self, record):
        current_log = (record.module, record.levelno, record.msg)
        if current_log == self.last_log:
            self.count += 1
            record.msg = f"{record.msg} (x{self.count})"
        else:
            self.last_log = current_log
            self.count = 1
        return True

class ColorFormatter(logging.Formatter):
    LEVEL_COLORS = {
        logging.DEBUG: "\x1b[36m",
        logging.INFO: "\x1b[32m",
        logging.WARNING: "\x1b[33m",
        logging.ERROR: "\x1b[31m",
        logging.CRITICAL: "\x1b[31;1m",
    }
    COLOR_RESET = "\x1b[0m"

    def format(self, record):
        color = self.LEVEL_COLORS.get(record.levelno, "")
        record.levelname = f"{color}{record.levelname:<8}{self.COLOR_RESET}"
        record.msg = f"{color}{record.msg}{self.COLOR_RESET}"
        return super().format(record)

def setup_console_logging(level=logging.INFO):
    logging.getLogger('comtypes').setLevel(logging.WARNING)

    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    root_logger.setLevel(level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    fmt = "[%(asctime)s.%(msecs)03d] [%(levelname)s] [%(module)s] %(message)s"
    datefmt = "%H:%M:%S"

    if hasattr(console_handler.stream, 'isatty') and console_handler.stream.isatty():
        formatter = ColorFormatter(fmt, datefmt=datefmt)
    else:
        formatter = logging.Formatter(fmt, datefmt=datefmt)

    console_handler.setFormatter(formatter)
    console_handler.addFilter(RepeatFilter())
    root_logger.addHandler(console_handler)