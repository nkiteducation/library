from contextlib import asynccontextmanager
import logging
import random
import uuid
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware


LOG = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    LOG.info("start")
    yield
    LOG.info("stop")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(lifespan=lifespan, default_response_class=ORJSONResponse)

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        messages = [
            "🚧 Oops! Something went wrong... We're already fixing it! 🔧🐛",
            "🔥 Fire! But not in a good way... The server is panicking! 🏃💨",
            "⚠️ Oops! Something broke. We're on our way! 🚀",
            "🤖 Beep-boop! The system crashed, but we're rebooting it... Hopefully. 🤞",
            "🤖 Uh-oh! Something went wrong... But don't worry, our server-bot is fixing it! 🔧⚡",
            "💥 Oh no! Something broke... But we promise to revive the server from the ashes! 🔥🛠️",
            "🧐 It's not a bug, it's a feature! Just not the one we wanted... Fixing it! 🔄🔧",
            "🐱‍💻 Our server cats are already working on a fix! Please be patient... 🛠️",
        ]

        error_id = str(uuid.uuid4())
        LOG.error(f"Unhandled error {error_id}: {exc}", exc_info=True)

        return ORJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "error_id": error_id,
                "message": random.choice(messages),
            },
        )

    app.add_middleware(GZipMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app
