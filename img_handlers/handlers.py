import cv2 as cv
import numpy as np
import faiss
from motor.motor_asyncio import AsyncIOMotorClient
from math import sqrt
from PIL import Image
import io

from db.db_crud import FaceCollection
from db.set_mongo import connect_to_mongodb
from config.config import logger
from utils import get_embedding


class FaceHandlers:
    def __init__(self, client: AsyncIOMotorClient):
        self.client = client
        self.emb_size = 512
        self.index = faiss.IndexFlatL2(self.emb_size)
        self.names = []
        
    async def _load_index(self):
        try:
            collection = FaceCollection(self.client)
            faces = await collection.find_all()
            embeddings = []
            self.names = []
            for face in faces:
                embedding = np.array(face["embedding"], dtype=np.float64)            
                normilize_embedding = embedding / np.linalg.norm(embedding)
                embeddings.append(normilize_embedding)
                
                name = face["name"]
                self.names.append(name)
            if embeddings:
                self.index.add(np.vstack(embeddings))
            print(self.names)
        except Exception as e:
            logger.error(f"Ошибка при загрузке в индекс {e}")

    async def save_face(self, person_name: str, img_bytes: bytes):
        try:
            collection = FaceCollection(self.client)
            
            buf = io.BytesIO(img_bytes)
            img = Image.open(buf)
            arr = np.array(img)
            embedding = get_embedding(arr)
            
            if await collection.find_one(person_name):
                logger.warning("Попытка добавления существующего пользователя")
                return None

            result = await collection.save(person_name, embedding.tolist(), img_bytes)
            logger.info(f"{person_name} добавлен в монго")         
            
            normilize_embedding = embedding / np.linalg.norm(embedding)
            self.index.add(np.array([normilize_embedding], dtype=np.float64))
            self.names.append(person_name)
            logger.info(f"{person_name} добавлен в индекс")    
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