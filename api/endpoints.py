from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Optional, Annotated
import logging
import cv2 as cv
from io import BytesIO
import numpy as np
from PIL import Image

from db.set_mongo import connect_to_mongodb
from db.db_crud import FaceCollection
from img_handlers.handlers import save_face, find_face
from api.models import Face
from utils import local_save
from config.config import logging

app = APIRouter(prefix="/faces")
logger = logging.getLogger(__name__)

@app.post("/add")
async def add_face(
    file: Annotated[UploadFile, File(...)],
    name: Annotated[str, Form(...)],
):
    bytes_file = await file.read()
    path, name = local_save(bytes_file, name)
    
    logging.debug(f"given to save: {name} -> {path}")    
    face_db = await save_face(name, path)
    if face_db:
        return JSONResponse({"face_id": f"{face_db.inserted_id}"}, status_code=201)
    raise HTTPException(status_code=500, detail="Vse govno")

COUNT = 0

@app.post("/find")
async def find_face_endpoint(
    file: Annotated[UploadFile, File(...)],
    threshold: Optional[float] = Form(.5),
):
    global COUNT
    COUNT += 1
    logger.error(f"COUNR REQUEST: {COUNT}")
    db = await connect_to_mongodb()
    if db is None:
        raise HTTPException(status_code=500, detail="Ошибка подключения к MongoDB")
    
    bytes_file = await file.read()
    buf = BytesIO(bytes_file)
    img = Image.open(buf)
    arr = np.array(img)
    person_name = await find_face(arr, threshold)

    if person_name:
        return {"name": person_name}
    else:
        return JSONResponse({"message": "Лицо не найдено."}, status_code=404)

@app.delete("/remove", status_code=204)
async def remove_face(
    face_id: Annotated[str, Form(...)]
):
    db = await connect_to_mongodb()
    if db is None:
        raise HTTPException(status_code=500, detail="Ошибка подключения к MongoDB")

    collection = FaceCollection(db)
    delete_result = await collection.delete(face_id)

    if delete_result:
        return 
    raise HTTPException(status_code=404, detail=f"Лицо с ID {face_id} не найдено.")


@app.put("/update", status_code=204)
async def update_face(
    face_id: Annotated[str, Form(...)],
    name: Annotated[str, Form(...)],
    file: Annotated[UploadFile, File(...)]
):
    db = await connect_to_mongodb()
    if db is None:
        raise HTTPException(status_code=500, detail="Ошибка подключения к MongoDB")
    collection = FaceCollection(db)
    
    image_bytes = await file.read()
    path, name = local_save(image_bytes, name)
    update_result = await collection.update(face_id, path, image_bytes)
    if update_result:
        return
    raise HTTPException(status_code=500, detail="Cann't update face")
