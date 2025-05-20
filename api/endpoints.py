from fastapi import APIRouter, File, UploadFile, Form, HTTPException, FastAPI
from fastapi.responses import JSONResponse
from pydantic import NaiveDatetime
from typing import Optional, Annotated, List
import logging
import cv2 as cv
from io import BytesIO
import numpy as np
from PIL import Image
from contextlib import asynccontextmanager
from deepface import DeepFace
from datetime import datetime
import re

from db.set_mongo import connect_to_mongodb
from api.models import NameModel, LogModel
from utils.api import local_save, transliterate
from config.config import logging
from img_handlers.handlers import FaceHandlers, FaceCollection


app = APIRouter()
logger = logging.getLogger(__name__)

CLIENT, face_handlers = None, None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global CLIENT, face_handlers
    CLIENT = connect_to_mongodb()
    face_handlers = FaceHandlers(CLIENT)
    await face_handlers._load_index()
    yield
    CLIENT.close()
    

@app.post("/faces/add")
async def add_face(
    file: Annotated[UploadFile, File(max_length=5242880)],
    name: Annotated[NameModel, Form(...)],
):
    bytes_file = await file.read()
    if len(bytes_file) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Файл слишком большой")
    path, name = local_save(bytes_file, name)
    
    logging.debug(f"given to save: {name} -> {path}")
    face_db = await face_handlers.save_face(name, path)
    if face_db:
        return JSONResponse({"face_id": f"{face_db.inserted_id}"}, status_code=201)
    raise HTTPException(status_code=500, detail="Vse govno")

@app.post("/faces/find")
async def find_face_endpoint(
    file: Annotated[UploadFile, File(...)],
    threshold: Optional[float] = Form(.5),
):  
    logger.debug(threshold)
    bytes_file = await file.read()
    if len(bytes_file) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Файл слишком большой")
    buf = BytesIO(bytes_file)
    img = Image.open(buf)
    arr = np.array(img)
    person_name, min_distance = face_handlers.find_face(arr, threshold)
    response = {"threshold": threshold, "min_distance": float(min_distance)}
    
    mongo = FaceCollection(CLIENT)
    if person_name:
        await mongo.write_log(person_name, True)
        response["name"] = person_name
        return JSONResponse(response)
    
    await mongo.write_log("неизвестный", False)
    response["message"] =  "Лицо не найдено"
    return JSONResponse(response, status_code=404)

@app.delete("/faces/remove", status_code=204)
async def remove_face(
    face_id: Annotated[str, Form(...)]
):
    collection = FaceCollection(CLIENT)
    delete_result = await collection.delete(face_id)

    if delete_result:
        return 
    raise HTTPException(status_code=404, detail=f"Лицо с ID {face_id} не найдено.")


@app.put("/faces/update", status_code=204)
async def update_face(
    face_id: Annotated[str, Form(...)],
    name: Annotated[NameModel, Form(...)],
    file: Annotated[UploadFile, File(...)]
):
    
    collection = FaceCollection(CLIENT)
    bytes_file = await file.read()
    if len(bytes_file) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Файл слишком большой")
    path, name = local_save(bytes_file, name)
    update_result = await collection.update(face_id, path, bytes_file)
    if update_result:
        return
    raise HTTPException(status_code=500, detail="Не удалось обновить запись")


@app.get("/log", response_model=List[LogModel])
async def get_logs( 
    start: datetime = None, 
    end: datetime = None,
    name: str = None
):
    logger.debug(f"\n\n\ntake rquest with {start, end, name}\n\n\n")
    query = {}
    if start and end:
        query["time"] = {"$gte": start, "$lte": end}
    elif start:
        query["time"] = {"$gte": start}
    elif end:
        query["time"] = {"$lte": end}
    if name:
        name = name.replace(" ", "_")
        if not re.match(r"^[A-Z][a-z]+_[A-Z][a-z]+$", name):
            raise HTTPException(status_code=422, detail="Не валидное имя пользователя")
        query["name"] = name
    
    logs = await FaceCollection(CLIENT).event_log.find(query).to_list()
    logger.debug(f"\n\n\n DANO: {logs} \n\n\n")
    return logs