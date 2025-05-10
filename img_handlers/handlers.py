from cv2.typing import MatLike
import cv2 as cv
import numpy as np
from bson.binary import Binary
from deepface import DeepFace
from faiss import IndexFlatL2


from db.db_crud import FaceCollection
from db.set_mongo import connect_to_mongodb
from config.config import logger
from utils.img_handlers import cosine_similarity, img_to_bytes, get_embedding


class FaceHandlers:
    async def initial(self, client):
        
        self.client = client
        self.emb_size = 512
        self.index = IndexFlatL2(self.emb_size)
        self.names = []
        await self._load_index()
        
    async def _load_index(self):
        try:
            collection = FaceCollection(self.client)
            faces = await collection.find_all()
            embeddings = []
            self.names = []
            for face in faces:
                embedding = np.array(face["embedding"], dtype=np.float64)
                embeddings.append(embedding)
                self.names.append(face["name"])
            if embeddings:
                embeddings = np.vstack(embeddings)
                self.index.add(embeddings)
        except Exception as e:
            logger.error(f"Ошибка при загрузке в индекс {e}")
    
    async def save_face(self, person_name: str, img_path: str):
        try:
            collection = FaceCollection(self.client)
            
            img = cv.imread(img_path)
            embedding = get_embedding(img_path).tolist()
            img_bytes = Binary(img_to_bytes(img))
            if await collection.collection.find_one({"name": person_name}):
                logger.warning("Попытка добавления существующего пользователя")
                return None

            result = await collection.save(person_name, embedding, img_bytes)
            
            
            self.index.add(np.array([embedding], dtype=np.float64))
            self.names.append(person_name)
            
            logger.info(f"{person_name} добавлен в монго")
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при добавлении пользователя: {e}")
            raise
        
            
    async def find_face(self, img: MatLike, threshhold=.5):
        try:
            collection = FaceCollection(self.client)
            embedding = get_embedding(img)
            
            distances, indices = self.index.search(np.array([embedding], dtype=np.float64), 1)
            distance = distances[0][0]
            index = indices[0][0]
            
            cosine_distance = 1 - (distance / 2)
            if cosine_distance < threshhold and index < len(self.names):
                logger.info("Пользователь найден")
                return self.names[index]
            logger.info("Пользователь НЕ найден")
            return None
        except Exception as e:
            logger.error(f"Ошибка при поиске лица: {e}")
            
            # async for face_data in collection.get_all():
            #     db_embedding = np.array([float(x) for x in face_data["embedding"]], np.float64)
            #     cur_dist = 1 - cosine_similarity(embedding, db_embedding)
                    
            #     logger.debug(f"ZXC:\n {cur_dist}\n\n\n")
                
            #     if cur_dist < min_distance:
            #         min_distance = cur_dist
            #         person = face_data["name"]
                    
            # if min_distance < threshhold:
            #     logger.info(f"Face find: {person}, min distance {min_distance}")
            #     return person
            # else:
            #     logger.info(f"Face not found, min distance {min_distance}")
            #     return None
    
    


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