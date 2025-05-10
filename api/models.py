from pydantic import BaseModel, field_validator
from typing import Annotated
from datetime import datetime
import re


class NameModel(BaseModel):
    name: str

    @field_validator("name")
    def validate_name(cls, v):
        if not re.match(r"^[a-zA-Z]+_[a-zA-Z]+$", v):
            raise ValueError("Имя должно содержать только буквы, пробелы или подчёркивания")
        return v
    
class LogModel(BaseModel):
    _id: str
    name: str
    time: datetime
    success: bool