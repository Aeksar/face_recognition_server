import cv2 as cv
import numpy as np
import faiss
from cryptography.fernet import Fernet
from motor.motor_asyncio import AsyncIOMotorClient
from math import sqrt
from PIL import Image
import io
import base64

from db.db_crud import FaceCollection
from db.set_mongo import connect_to_mongodb
from config.config import logger, Settings
from utils import get_embedding


class FaceHandlers:
    def __init__(self, client: AsyncIOMotorClient):
        self.face_col = FaceCollection(client)
        emb_size = 512
        self.index = faiss.IndexFlatL2(emb_size)
        self.names = []
        key = base64.urlsafe_b64encode(Settings().SECRET_KEY)
        self.cipher = Fernet(key)
        
    async def _load_index(self):
        try:
            faces = await self.face_col.find_all()
            embeddings = []
            self.names = []
            for face in faces:
                encrypt_emb = face["embedding"]
                embedding = self.decrypt_embedding(encrypt_emb)
                normilize_embedding = embedding / np.linalg.norm(embedding)
                embeddings.append(normilize_embedding)
                self.names.append(face["name"])
                
            if embeddings:
                self.index.add(np.vstack(embeddings))
            print(self.names)
        except Exception as e:
             logger.error(f"Ошибка при загрузке в индекс {e}")

    async def save_face(self, person_name: str, img_bytes: bytes):
        try:    
            buf = io.BytesIO(img_bytes)
            img = Image.open(buf)
            arr = np.array(img)
            embedding = get_embedding(arr)
            encrypt_emb = self.encrypt_embedding(embedding)
            
            if await self.face_col.find_one(person_name):
                logger.warning("Попытка добавления существующего пользователя")
                return None       
            
            normilize_embedding = embedding / np.linalg.norm(embedding)
            self.index.add(np.array([normilize_embedding], dtype=np.float64))
            self.names.append(person_name)
            logger.info(f"{person_name} добавлен в индекс")  
            
            result = await self.face_col.save(person_name, encrypt_emb)
            logger.info(f"{person_name} добавлен в монго")    
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при добавлении пользователя: {e}")
            raise
        
            
    def find_face(self, img: np.ndarray, threshhold=.5):
        try:
            embedding = get_embedding(img)
            normilize_embedding = embedding / np.linalg.norm(embedding)
            distances, indices = self.index.search(np.array([normilize_embedding], dtype=np.float64), 1)
            distance = distances[0][0]
            index = indices[0][0]
            
            normilize_distance = distance / sqrt(512) * 10
            if normilize_distance < threshhold and index < len(self.names):
                logger.info("Пользователь найден")
                return self.names[index], normilize_distance
            logger.info("Пользователь НЕ найден")
            return None, normilize_distance

        except Exception as e:
            logger.error(f"Ошибка при поиске лица: {e}")
            raise
        
    def encrypt_embedding(self, embedding: np.ndarray) -> bytes:
        emb_bytes = embedding.tobytes()
        encrypt_emb = self.cipher.encrypt(emb_bytes)
        return encrypt_emb
    
    def decrypt_embedding(self, encrypt_data: bytes):
        decrypt_emb = self.cipher.decrypt(encrypt_data)
        res = np.frombuffer(decrypt_emb, dtype=np.float64)
        return res

        

if __name__ == "__main__":
    
    import asyncio
    
    async def main():
        db = await connect_to_mongodb()
        if db is not None:
            collection = db["faces"]
            # await save_face(collection, "Vladimir Putin", "images/Vladimir_Putin.jpg")
            # await save_face(collection, "Joe Biden", "images/joe_Biden.jpg")
            
            
            img1 = cv.imread("images/Test_JB.jpg")
            img2 = cv.imread("images/Test_VVP.jpg")
            img3 = cv.imread("images/Test_Donald.jpg")
            # await find_face(collection, img1, metric="cosine")
            await FaceHandlers().find_face(collection, img2, metric="cosine")
            # await find_face(collection, img3, metric="cosine")
            
    asyncio.run(main())