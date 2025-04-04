import aiofiles
from pathlib import Path
from typing import AsyncGenerator, BinaryIO


class FileManager:
    TEMP_FOLDER = Path("temp").resolve()
    CHUNK_SIZE = 4096

    @classmethod
    async def reading(cls, name: str, file: BinaryIO):
        cls.TEMP_FOLDER.mkdir(exist_ok=True)
        async with aiofiles.open(cls.TEMP_FOLDER / name, "wb") as f:
            while chunk := await file.read(cls.CHUNK_SIZE):
                await f.write(chunk)

        return cls.TEMP_FOLDER / name

    @classmethod
    async def writing(cls, path: str) -> AsyncGenerator[bytes, None]:
        async with aiofiles.open(path, "rb") as f:
            while chunk := await f.read(cls.CHUNK_SIZE):
                yield chunk
