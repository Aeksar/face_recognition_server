from motor.motor_asyncio import AsyncIOMotorClient
from bson.binary import Binary
from bson.objectid import ObjectId
from bson.datetime_ms import DatetimeMS
from datetime import datetime

from config.config import logger
from utils import get_embedding

class FaceCollection:
    
    def __init__(self, client: AsyncIOMotorClient):
        self.client = client
        self.db = self.client["face_recognition"]
        self.collection = self.db["faces"]
        self.event_log = self.db["event_log"]
        
    async def find_one(self, person_name: str):
        result = await self.collection.find_one({"name": person_name})
        return result
    
    async def save(self, person_name: str, embedding: list[float], image_bytes: bytes):
        try:
            image = Binary(image_bytes)
            face_data = {
                "name": person_name,
                "embedding": embedding,
                "image": image,
            }
            result = await self.collection.insert_one(face_data)
            return result
        except Exception as e:
            logger.error(f"Oshibka: {e}")
    
    async def find_all(self):
        result = await self.collection.find().to_list()
        return result
    
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

    async def write_log(self, name: str, success: bool):
        res = await self.event_log.insert_one({
            "name": name,
            "time": DatetimeMS(datetime.now()),
            "success": success
        })
        
        logger.debug(f"\n\n\nLOG WRITED: {res} \n\n\n\n")
    