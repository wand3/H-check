import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import h_check_router
import uvicorn
from app.database.db_engine import db_lifespan, connect_to_mongo, close_mongo_connection
from .logger import logger
from fastapi.staticfiles import StaticFiles
from pathlib import Path


def create_app() -> FastAPI:
    app: FastAPI = FastAPI(db_lifespan=db_lifespan)
    logger.info(f'Application started -----------')


    origins = [
        "http://localhost:5173/",
        "http://127.0.0.1:8000/*",
        "*"
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    # Include routes
    app.include_router(h_check_router, tags=["FHIR"])


    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

