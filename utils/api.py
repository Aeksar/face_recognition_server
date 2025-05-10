def local_save(img_bytes: bytes, name: str):
    name = name.strip().replace(" ", "_")
    path = f"images/{name}.jpg"
    
    with open(path, "wb") as f:
        f.write(img_bytes)
        
    return path, name