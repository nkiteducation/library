from pydantic import ByteSize
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class BasaSetting(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="src/.env",
        env_file_encoding="utf-8",
        env_nested_delimiter="_",
        extra="ignore",
        frozen=True
    )

class DataBaseSetting(BasaSetting):
    DRIVERNAME: str
    USERNAME: str | None = None
    PASSWORD: str | None = None
    HOST: str | None = None
    PORT: str | None = None
    DATABASENAME: str

    @property
    def URL(self) -> URL:
        if "sqlite" in self.DRIVERNAME:
            return URL.create(drivername=self.DRIVERNAME, database=self.DATABASENAME)
        elif all([self.USERNAME, self.PASSWORD, self.HOST, self.PORT]):
            return URL.create(
                self.DRIVERNAME,
                self.USERNAME,
                self.PASSWORD,
                self.HOST,
                self.PORT,
                self.DATABASENAME,
            )
        raise ValueError("Не хватает данных для создания URL")

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
    DATABASE: DataBaseSetting


appSetting = AppSetting()
