import os
import gzip
import logging
import pytest
from logging.handlers import RotatingFileHandler
from pathlib import Path
from io import StringIO
from core.logger import ZipRotatingFileHandler, setup_console_logging, setup_file_logging, configure_logging, BlacklistFilter

# Тестируем ZipRotatingFileHandler
@pytest.fixture
def zip_rotating_file_handler():
    log_file = "test.log"
    handler = ZipRotatingFileHandler(filename=log_file, maxBytes=10, backupCount=2)
    yield handler
    if os.path.exists(log_file):
        os.remove(log_file)
    for i in range(1, 3):
        backup_file = f"{log_file}.{i}.gz"
        if os.path.exists(backup_file):
            os.remove(backup_file)

def test_zip_rotating_file_handler_rollover(zip_rotating_file_handler):
    # Запишем данные в лог и проверим, что происходит ротация
    log_file = zip_rotating_file_handler.baseFilename
    log_message = "Test log message"
    
    # Записываем лог
    zip_rotating_file_handler.emit(logging.LogRecord("test", logging.DEBUG, "", 0, log_message, [], None))
    
    # Проверим, что лог был записан
    with open(log_file, 'r') as f:
        content = f.read()
        assert log_message in content

    # Эмулируем ротацию
    zip_rotating_file_handler.doRollover()

    # Проверим наличие сжатого файла
    backup_file = f"{log_file}.1.gz"
    assert os.path.exists(backup_file)
    
    # Проверим, что файл был сжат
    with gzip.open(backup_file, 'rb') as f:
        backup_content = f.read().decode('utf-8')
        assert log_message in backup_content


# Тестируем BlacklistFilter
@pytest.fixture
def blacklist_filter():
    blacklist = {"blacklisted_logger"}
    filter = BlacklistFilter(blacklist=blacklist)
    yield filter

def test_blacklist_filter(blacklist_filter):
    logger = logging.getLogger("blacklisted_logger")
    logger.addFilter(blacklist_filter)
    
    # Логируем сообщение, которое должно быть заблокировано
    log_stream = StringIO()
    stream_handler = logging.StreamHandler(log_stream)
    logger.addHandler(stream_handler)
    
    logger.warning("This should not appear")
    
    # Проверим, что сообщение не было записано
    output = log_stream.getvalue()
    assert "This should not appear" not in output


# Тестируем настройку логирования для консоли и файла
@pytest.fixture
def configure_logging_fixture():
    configure_logging(level=logging.DEBUG)
    yield
    # Очистим конфигурацию логирования после теста
    logging.root.handlers.clear()

def test_console_logging(configure_logging_fixture):
    log_stream = StringIO()
    stream_handler = logging.StreamHandler(log_stream)
    logging.getLogger().addHandler(stream_handler)
    
    logging.info("Console log message")
    
    # Проверим, что сообщение появилось в выводе
    output = log_stream.getvalue()
    assert "Console log message" in output

def test_file_logging(configure_logging_fixture):
    log_file = Path("logs") / "message.log"
    log_message = "File log message"
    
    logging.info(log_message)
    
    # Проверим, что сообщение записано в файл
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert log_message in content
    
    # Удалим файл после теста
    if os.path.exists(log_file):
        os.remove(log_file)
