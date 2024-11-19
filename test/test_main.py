from fastapi.testclient import TestClient
from fastapi import status
from .. import main

client = TestClient(main.app)

def test_healthy():
    responce = client.get('/healthy')
    assert responce.status_code == status.HTTP_200_OK
    assert responce.json() == {"status": "Healthy"}

