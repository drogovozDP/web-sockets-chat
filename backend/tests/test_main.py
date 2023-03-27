from fastapi.testclient import TestClient

from backend.src.main import app

client = TestClient(app)


# def test_foo():
#     a = client.get("/chat")
#     print(a)
#     assert True
