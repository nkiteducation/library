from core.setting import AppSetting


def test_app_settings(monkeypatch):
    monkeypatch.setenv("DEVELOPMENT", "true")
    monkeypatch.setenv("API_HOST", "127.0.0.1")
    monkeypatch.setenv("API_PORT", "8000")
    monkeypatch.setenv("API_WORKERS", "2")
    monkeypatch.setenv("LOGGER_LEVEL", "DEBUG")
    monkeypatch.setenv("LOGGER_MAXBYTES", "1048576")
    monkeypatch.setenv("LOGGER_BACKUPCOUNT", "5")
    monkeypatch.setenv("LOGGER_BLACKLIST", "uvicorn,gunicorn")
    monkeypatch.setenv("DATABASE_DRIVERNAME", "sqlite+aiosqlite")
    monkeypatch.setenv("DATABASE_DATABASENAME", "memory.db")

    settings = AppSetting()

    assert settings.DEVELOPMENT is True
    assert settings.API.HOST == "127.0.0.1"
    assert settings.API.PORT == 8000
    assert settings.API.WORKERS == 2
    assert settings.LOGGER.LEVEL == "DEBUG"
    assert settings.LOGGER.MAXBYTES == 1048576
    assert settings.LOGGER.BACKUPCOUNT == 5
    assert settings.LOGGER.BLACKSET == {"uvicorn", "gunicorn"}
    assert settings.DATABASE.DRIVERNAME == "sqlite+aiosqlite"
    assert settings.DATABASE.DATABASENAME == "memory.db"
    assert str(settings.DATABASE.URL) == "sqlite+aiosqlite:///memory.db"
