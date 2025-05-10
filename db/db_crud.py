from cv2.typing import MatLike
import cv2 as cv
import numpy as np
import asyncio
import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from bson.binary import Binary
from bson.objectid import ObjectId
from typing import Optional


from db.set_mongo import connect_to_mongodb
from config.config import logger
from utils import get_embedding

class FaceCollection:
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.get_collection("faces")
    
    async def save(self, person_name: str, embedding: list[float], image_bytes: bytes):
        try:
            face_data = {
                "name": person_name,
                "embedding": embedding,
                "image": image_bytes,
            }
            result = await self.collection.insert_one(face_data)
            return result
        except Exception as e:
            logger.error(f"Oshibka: {e}")
    
    def get_all(self):
        return self.collection.find()
    
    async def delete(self, id):
        res = await self.collection.delete_one({"_id": ObjectId(id)})
        if res.deleted_count > 0:
            return True
        return False
    
    async def update(
        self, 
        id: str,  
        path: str, 
        image_bytes: bytes
        ):
        logger.debug(f"DANO: {path}")
        embedding = get_embedding(path).tolist()
        img = Binary(image_bytes)
        if id:
            update_result = await self.collection.update_one(
                {"_id": ObjectId(id)},
                {"$set": {"embedding": embedding, "image": img}}
            )
        logger.debug(f"CHANGED: {update_result}, {update_result.modified_count, update_result.matched_count}")
        
        if update_result.matched_count > 0:
            return True
        return False