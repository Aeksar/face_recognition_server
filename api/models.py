from pydantic import BaseModel, field_validator
from datetime import datetime
import re


class NameModel(BaseModel):
    name: str

    @field_validator("name")
    def validate_name(cls, v: str):
        v = v.strip()
        if not re.match(r"^[a-zA-Zа-яА-Я]+_[a-zA-Zа-яА-Я]+$", v):
            raise ValueError("Имя должно содержать только буквы и нижнее подчёркивание")
        return v  
    
class LogModel(BaseModel):
    _id: str
    name: str
    time: datetime
    success: bool