from pydantic import BaseModel

class Face(BaseModel):
    _id: str
    name: str
    embedding: list[float]
    image: bytes