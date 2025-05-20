import numpy as np
import cv2 as cv
from cv2.typing import MatLike
from numpy.typing import ArrayLike
from typing import Union
from deepface import DeepFace


def img_to_bytes(img: MatLike):
    ok, encoded_img = cv.imencode(".jpg", img)
    if ok:
        return encoded_img.tobytes()
    raise ValueError(f"cannot convert to bytes {img}")

def get_embedding(img_path: Union[str, np.ndarray]):
    embedding = DeepFace.represent(img_path=img_path, model_name="ArcFace", detector_backend="mtcnn")
    embedding = np.array([float(x) for x in embedding[0].get("embedding")])
    return embedding