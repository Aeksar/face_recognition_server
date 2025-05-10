from fastapi import APIRouter, File, UploadFile, Form, HTTPException, FastAPI
from fastapi.responses import JSONResponse
from typing import Optional, Annotated
import logging
import cv2 as cv
from io import BytesIO
import numpy as np
from PIL import Image
from contextlib import asynccontextmanager
from deepface import DeepFace

from db.set_mongo import connect_to_mongodb
from db.db_crud import FaceCollection
from api.models import Face
from utils.api import local_save, get_face_handlers
from config.config import logging


app = APIRouter(prefix="/faces")
logger = logging.getLogger(__name__)

CLIENT = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global CLIENT
    CLIENT = connect_to_mongodb()
    yield
    CLIENT.close()
    

@app.post("/add")
async def add_face(
    file: Annotated[UploadFile, File(...)],
    name: Annotated[str, Form(...)],
):
    bytes_file = await file.read()
    path, name = local_save(bytes_file, name)
    
    logging.debug(f"given to save: {name} -> {path}")  
    face_handlers = await get_face_handlers(CLIENT)
    face_db = await face_handlers.save_face(name, path)
    if face_db:
        return JSONResponse({"face_id": f"{face_db.inserted_id}"}, status_code=201)
    raise HTTPException(status_code=500, detail="Vse govno")

@app.post("/find")
async def find_face_endpoint(
    file: Annotated[UploadFile, File(...)],
    threshold: Optional[float] = Form(.5),
):  
    bytes_file = await file.read()
    buf = BytesIO(bytes_file)
    img = Image.open(buf)
    arr = np.array(img)
    face_handlers = await get_face_handlers(CLIENT)
    person_name = await face_handlers.find_face(arr, threshold)

    if person_name:
        return {"name": person_name}
    else:
        return JSONResponse({"message": "Лицо не найдено."}, status_code=404)

@app.delete("/remove", status_code=204)
async def remove_face(
    face_id: Annotated[str, Form(...)]
):

    collection = FaceCollection(CLIENT)
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
    
    collection = FaceCollection(CLIENT)
    image_bytes = await file.read()
    path, name = local_save(image_bytes, name)
    update_result = await collection.update(face_id, path, image_bytes)
    if update_result:
        return
    raise HTTPException(status_code=500, detail="Cann't update face")
