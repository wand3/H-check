import logging

from fastapi.testclient import TestClient
from pymongo import MongoClient
import pytest
from webapp.main import app


@pytest.fixture(scope="session")
def db_client():
    """Provide a connection to the MongoDB test database."""
    client = MongoClient('mongodb://localhost:27017')
    db = client["ethos"]
    yield db
    client.close()  # Close the MongoClient connection


@pytest.fixture(scope="function")
def clear_db(db_client):
    """Clear the database and ensure the 'users' collection exists."""
    # Drop the collection if it exists
    if "users" in db_client.list_collection_names():
        db_client.drop_collection("users")
    # Create the 'users' collection for testing
    db_client.create_collection("users")
    yield
    # Cleanup after the test
    db_client.drop_collection("users")


@pytest.fixture(scope="function")
def client():
    """Provide a test client for FastAPI."""
    with TestClient(app) as c:
        yield c


def get_recrent_model(client, collection_name: str):
    collection = client[f"{collection_name}"]
    # logging.info(f"projects collectioncollectioncollection  {collection}")

    post_cursor = collection.find()
    # logging.info(f"projects collection  {post_cursor}")
    all_p = list(post_cursor)
    from tests.test_blog import convert_objectid_to_str
    post_cursor = convert_objectid_to_str(posts=all_p)  # convert the object ids to string
    expected_posts = post_cursor
    return expected_posts

