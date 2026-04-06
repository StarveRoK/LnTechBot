from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class SendMessage(BaseModel):
    chat_id: str
    text: str
    image_ids: Optional[list[str]] = None
    new_files: Optional[list] = None

    @field_validator("image_ids", mode='before')
    def check_image_ids(cls, value):
        if value and isinstance(value, list):
            return [str(item) for item in value]
        return None