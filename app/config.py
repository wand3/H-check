import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY: str = 'ONE'
    ALGORITHM: str = "HS256"
    DATABASE_URI = os.getenv('CLUSTER') or 'mongodb://127.0.0.1:27017/'
