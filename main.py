import uvicorn
from fastapi import FastAPI

from api.endpoints import app, lifespan


api = FastAPI(lifespan=lifespan, title="Face Recognition API")
api.include_router(app)

if __name__ == "__main__":
    uvicorn.run(api)