from app.factorial_utils import factorial
from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)


# ----------- Unit tests for factorial() function -----------

def test_factorial_of_zero():
    assert factorial(0) == 1


def test_factorial_of_one():
    assert factorial(1) == 1


def test_factorial_positive():
    assert factorial(5) == 120
    assert factorial(10) == 3628800


def test_factorial_negative():
    with pytest.raises(ValueError):
        factorial(-3)


# ----------- Integration tests for API endpoint -----------

def test_api_factorial_success():
    response = client.post("/factorial", json={"number": 5})
    assert response.status_code == 200
    assert response.json()["result"] == "120"


def test_api_factorial_zero():
    response = client.post("/factorial", json={"number": 0})
    assert response.status_code == 200
    assert response.json()["result"] == "1"


# def test_api_factorial_decimal():
#     response = client.post("/factorial", json={"number": 4.5})
#     assert response.status_code == 422
#     assert response.json()["result"] == "1"


def test_api_factorial_invalid():
    response = client.post("/factorial", json={"number": -2})
    assert response.status_code == 422
    assert "greater than or equal to 0" in response.json()["detail"]
