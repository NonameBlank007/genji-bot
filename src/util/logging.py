import logging

logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s: [%(levelname)s] (%(name)s): %(message)s",
)


class ColouredFormat(logging.Formatter):
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    green = "\x1b[0;32m"
    purple = "\x1b[2;35m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format_str = "%(asctime)s: [%(levelname)s] (%(name)s): %(message)s"

    FORMATS = {
        logging.DEBUG: logging.Formatter(purple + format_str + reset),
        logging.INFO: logging.Formatter(green + format_str + reset),
        logging.WARNING: logging.Formatter(yellow + format_str + reset),
        logging.ERROR: logging.Formatter(red + format_str + reset),
        logging.CRITICAL: logging.Formatter(bold_red + format_str + reset),
    }

    def format(self, record):
        return self.FORMATS[record.levelno].format(record)


class HttpxFilter(logging.Filter):
    def filter(self, record):
        return not (record.name.startswith("httpx") and record.levelno <= logging.INFO)


logger = logging.getLogger(__name__)

handler = logging.StreamHandler()
handler.setFormatter(ColouredFormat())
handler.addFilter(HttpxFilter())

logger.root.addHandler(handler)
