from cv2.typing import MatLike
import cv2 as cv
import numpy as np
from bson.binary import Binary
from deepface import DeepFace

from db.db_crud import FaceCollection
from db.set_mongo import connect_to_mongodb
from config.config import logger
from utils import cosine_similarity, img_to_bytes, get_embedding


async def save_face(person_name: str, img_path: str):
    try:
        db = await connect_to_mongodb()
        collection = FaceCollection(db)
        
        img = cv.imread(img_path)
        embedding = get_embedding(img_path).tolist()
        img_bytes = Binary(img_to_bytes(img))

        result = await collection.save(person_name, embedding, img_bytes)
        logger.info(f"{result} saved in mongo")
        return result
        
    except Exception as e:
        logger.error(f"Error with save face: {e}")
        raise
       
        
async def find_face(img: MatLike, threshhold=.5,):
    try:
        db = await connect_to_mongodb()
        collection = FaceCollection(db)
        embedding = get_embedding(img)
        
        min_distance = float("inf")
        person = None
        
        async for face_data in collection.get_all():
            db_embedding = np.array([float(x) for x in face_data["embedding"]], np.float64)
            cur_dist = 1 - cosine_similarity(embedding, db_embedding)
                
            logger.debug(f"ZXC:\n {cur_dist}\n\n\n")
            
            if cur_dist < min_distance:
                min_distance = cur_dist
                person = face_data["name"]
                
        if min_distance < threshhold:
            logger.info(f"Face find: {person}, min distance {min_distance}")
            return person
        else:
            logger.info(f"Face not found, min distance {min_distance}")
            return None
        
    except Exception as e:
        logger.error(f"Error with find face: {e}")
        return None
    


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
            await find_face(collection, img2, metric="cosine")
            # await find_face(collection, img3, metric="cosine")
            
    asyncio.run(main())