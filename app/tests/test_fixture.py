from sqlmodel import SQLModel
import pytest
from sqlalchemy_utils import create_database, drop_database, database_exists
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, declarative_base
from sqlalchemy.orm.session import close_all_sessions


TEST_DATABASE_URL = "postgresql+asyncpg://postgres:ma3str0@localhost:5432/testhcheck"
fixture_used = False

@pytest.fixture(scope='session', autouse=True)
def create_and_delete_database():
    global fixture_used
    if fixture_used:
        yield
        return
    if database_exists(TEST_DATABASE_URL):
        drop_database(TEST_DATABASE_URL)
        create_database(TEST_DATABASE_URL)

    test_engine = create_engine(TEST_DATABASE_URL)
    SQLModel.metadata.create_all(bind=test_engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    TestDatabase(session=SessionLocal()).populate_test_database()
    fixture_used =True
    yield
    close_all_sessions()

    drop_database(TEST_DATABASE_URL)