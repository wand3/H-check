from typing import AsyncGenerator
from ..config import Config
from fastapi import FastAPI
from pymongo import AsyncMongoClient
import logging
from contextlib import asynccontextmanager


# MongoDB's connection string (localhost, no authentication)
# MONGO_CONNECTION_STRING = "mongodb://127.0.0.1:27017/"
MONGO_CONNECTION_STRING = Config.DATABASE_URI
DATABASE_NAME = "H-check"
# Load the MongoDB connection string from the environment variable MONGODB_URI

# Create a MongoDB client
client = AsyncMongoClient(MONGO_CONNECTION_STRING)
db = client["check"]


@asynccontextmanager
async def db_lifespan(app: FastAPI):
    # Startup
    app.mongodb_client = AsyncMongoClient(MONGO_CONNECTION_STRING)
    app.database = app.mongodb_client.get_default_database(DATABASE_NAME)
    ping_response = await app.database.command("ping")
    if int(ping_response["ok"]) != 1:
        raise Exception("Problem connecting to database cluster.")
    else:
        logging.info("Connected to database cluster.")

    yield

    # Shutdown
    await app.mongodb_client.close()

# Create a global client instance (do this ONCE at application startup)
# client: AsyncMongoClient = None


async def connect_to_mongo():
    global client
    if client is None:
        client = AsyncMongoClient(MONGO_CONNECTION_STRING)


async def close_mongo_connection():
    global client
    if client:
        await client.close()


async def get_db() -> AsyncGenerator:
    """
    Asynchronous dependency injection for MongoDB database.
    """
    if client is None:
        raise RuntimeError("MongoDB client not initialized. Call connect_to_mongo() on startup.")
    try:
        # db = client['ethos']  # Gets the default database from the URI
        yield db
    except Exception as e:
        raise f'{e}' # Re-raise the exception to be handled by FastAPI
    finally:
        pass # Motor handles connect
