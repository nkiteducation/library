from pydantic import ByteSize
from sqlalchemy import String, TypeDecorator


class SizeType(TypeDecorator):
    impl = String

    def process_bind_param(self, value: int, dialect: str) -> str:
        if not isinstance(value, int):
            raise ValueError(f"Некорректное значение размера: {value}")
        return ByteSize(value).human_readable()

    def process_result_value(self, value: str | None, dialect: str) -> int | None:
        if value is not None:
            return int(ByteSize(value))
        return None
