import uvicorn
from core.app import create_app
from core.setting import appSetting

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=appSetting.API.HOST,
        port=appSetting.API.PORT,
        workers=appSetting.API.WORKERS,
    )
