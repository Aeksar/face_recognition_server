from pydantic import BaseModel, field_validator
import re

class NameModel(BaseModel):
    name: str

    @field_validator("name")
    def validate_name(cls, v):
        if not re.match(r"^[a-zA-Z\s_]+$", v):
            raise ValueError("Имя должно содержать только буквы, пробелы или подчёркивания")
        return v