from pydantic import ByteSize
from pydantic_settings import BaseSettings, SettingsConfigDict


class BasaSetting(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="src/.env",
        env_file_encoding="utf-8",
        env_nested_delimiter="_",
        extra="ignore",
    )


class LoggerSetting(BasaSetting):
    LEVEL: str
    MAXBYTES: ByteSize
    BACKUPCOUNT: int
    BLACKLIST: str

    @property
    def BLACKSET(self) -> set[str]:
        return set(self.BLACKLIST.replace(" ", "").split(","))


class APISetting(BasaSetting):
    HOST: str
    PORT: int
    WORKERS: int


class AppSetting(BasaSetting):
    DEVELOPMENT: bool

    API: APISetting
    LOGGER: LoggerSetting


appSetting = AppSetting()
