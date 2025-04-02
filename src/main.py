import uvicorn
from core.app import create_app
from core.setting import appSetting
from api.v1 import v1_router

app = create_app()
app.include_router(v1_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=appSetting.API.HOST,
        port=appSetting.API.PORT,
        workers=appSetting.API.WORKERS,
    )
