from img_handlers.handlers import FaceHandlers

def local_save(img_bytes: bytes, name: str):
    name = name.strip().replace(" ", "_")
    path = f"images/{name}.jpg"
    
    with open(path, "wb") as f:
        f.write(img_bytes)
        
    return path, name

async def get_face_handlers(client):
    face_hadlers = FaceHandlers()
    await face_hadlers.initial(client)
    return face_hadlers