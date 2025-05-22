import uvicorn
from fastapi import FastAPI

from api.endpoints import app, lifespan


api = FastAPI(lifespan=lifespan)
api.include_router(app)

if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0")