from cv2.typing import MatLike
import cv2 as cv
import numpy as np
from bson.binary import Binary
from deepface import DeepFace
import faiss
from motor.motor_asyncio import AsyncIOMotorClient
from math import sqrt

from db.db_crud import FaceCollection
from db.set_mongo import connect_to_mongodb
from config.config import logger
from utils.img_handlers import img_to_bytes, get_embedding


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

    async def save_face(self, person_name: str, img_path: str):
        try:
            collection = FaceCollection(self.client)
            
            img = cv.imread(img_path)
            embedding = get_embedding(img_path).tolist()
            img_bytes = Binary(img_to_bytes(img))
            
            if await collection.find_one({"name": person_name}):
                logger.warning("Попытка добавления существующего пользователя")
                return None

            result = await collection.save(person_name, embedding, img_bytes)
            logger.info(f"{person_name} добавлен в монго")         
            
            self.index.add(np.array([embedding], dtype=np.float64))
            self.names.append(person_name)
            logger.info(f"{person_name} добавлен в индекс")    
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при добавлении пользователя: {e}")
            raise
        
            
    def find_face(self, img: np.ndarray, threshhold=.5):
        try:
            detected_imgs = DeepFace.represent(img_path=img, model_name="ArcFace", detector_backend="mtcnn")
            embedding = np.array([float(x) for x in detected_imgs[0].get("embedding")])
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