import gzip
import logging
import os
import shutil
from logging.handlers import RotatingFileHandler
from pathlib import Path

import colorlog


class BlacklistFilter(logging.Filter):
    def __init__(self, blacklist: set[str]) -> None:
        super().__init__()
        self.blacklist = blacklist

    def filter(self, record: logging.LogRecord) -> bool:
        return record.name not in self.blacklist


class ZipRotatingFileHandler(RotatingFileHandler):
    def doRollover(self) -> None:
        if self.stream:
            self.stream.close()
            self.stream = None

        if self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                src = self.rotation_filename(f"{self.baseFilename}.{i}.gz")
                dst = self.rotation_filename(f"{self.baseFilename}.{i + 1}.gz")
                if os.path.exists(src):
                    os.replace(src, dst)

            last_backup = self.rotation_filename(f"{self.baseFilename}.1")
            if os.path.exists(last_backup):
                os.remove(last_backup)
            self._rotate(self.baseFilename, last_backup)

        if not self.delay:
            self.stream = self._open()

    def _rotate(self, src: str, dst: str) -> None:
        self.rotate(src, dst)
        with open(dst, "rb") as fsrc, gzip.open(dst + ".gz", "wb") as fdst:
            shutil.copyfileobj(fsrc, fdst)
        os.remove(dst)


def setup_console_logging(level: int | str) -> None:
    console_handler = colorlog.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = colorlog.ColoredFormatter(
        "%(log_color)s[%(levelname)-8s] %(black)s%(name)s|%(funcName)s%(reset)s - "
        "%(reset)s%(cyan)s%(message)s%(reset)s",
        datefmt=None,
        reset=True,
        log_colors={
            "DEBUG": "blue",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
    )
    console_handler.setFormatter(console_formatter)
    logging.root.addHandler(console_handler)


def setup_file_logging(
    level: int | str,
    max_bytes: int = 10**6,
    backup_count: int = 5,
    delay: bool = True,
) -> None:
    logs_folder = Path("logs").resolve()
    logs_folder.mkdir(exist_ok=True)
    log_file = (logs_folder / "message").with_suffix(".log")
    file_handler = ZipRotatingFileHandler(
        filename=log_file,
        mode="a",
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
        delay=delay,
    )
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(
        "%(asctime)s - [%(levelname)-8s] - PID: %(process)d - "
        "%(name)s|%(funcName)s - %(message)s - %(filename)s:%(lineno)d"
    )
    file_handler.setFormatter(file_formatter)
    logging.root.addHandler(file_handler)


def configure_logging(
    level: int | str = logging.DEBUG,
    max_bytes: int = 10**6,
    backup_count: int = 5,
    delay: bool = True,
    blacklist: set[str] = None,
) -> None:
    """
    Общая конфигурация логирования:
      - Логирование с полными данными в файл
      - Простое и цветное логирование в консоль
    """
    logging.root.setLevel(logging.NOTSET)

    for i in blacklist:
        logging.getLogger(i).setLevel(logging.WARNING)

    setup_console_logging(level)
    setup_file_logging(level, max_bytes, backup_count, delay)
