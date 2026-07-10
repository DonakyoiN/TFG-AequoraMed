import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c
