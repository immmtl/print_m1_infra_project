from fastapi.testclient import TestClient

from app_final import app, APP_VERSION, DEFAULT_PASSWORD_LENGTH


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version():
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == {"version": APP_VERSION}


def test_criteria():
    response = client.get("/criteria")
    assert response.status_code == 200
    assert "length" in response.json()
    assert "not_common" in response.json()


def test_strong_password():
    response = client.post("/check", json={"password": "M8!vR2#pL9@x"})
    assert response.status_code == 200
    result = response.json()
    assert result["level"] == "strong"
    assert result["score"] == result["max_score"]
    assert result["recommendations"] == []
    assert "password" not in result


def test_common_password():
    response = client.post("/check", json={"password": "Password123"})
    assert response.status_code == 200
    result = response.json()
    assert result["level"] == "weak"
    assert result["checks"]["not_common"] is False
    assert result["recommendations"]


def test_short_password():
    response = client.post("/check", json={"password": "Ab7!"})
    assert response.status_code == 200
    result = response.json()
    assert result["level"] == "weak"
    assert result["checks"]["length"] is False


def test_sequence_and_repeats():
    for ending, criterion in (("4321", "no_sequences"), ("QwEr", "no_sequences"), ("AaA", "no_repeats")):
        response = client.post("/check", json={"password": "M8!vR2#pL9@x" + ending})
        assert response.status_code == 200
        result = response.json()
        assert result["level"] == "medium"
        assert result["checks"][criterion] is False
        assert result["score"] == result["max_score"] - 1


def test_invalid_password():
    for data in ({}, {"password": ""}, {"password": "x" * 257}, {"password": 123}):
        response = client.post("/check", json=data)
        assert response.status_code == 422


def test_generate_password():
    for length in (12, 20, 128):
        response = client.post("/generate", json={"length": length})
        assert response.status_code == 200
        result = response.json()
        assert result["length"] == length
        assert len(result["password"]) == length
        check = client.post("/check", json={"password": result["password"]})
        assert check.status_code == 200
        assert check.json()["level"] == "strong"


def test_generate_default_length():
    response = client.post("/generate", json={})
    assert response.status_code == 200
    assert len(response.json()["password"]) == DEFAULT_PASSWORD_LENGTH


def test_invalid_length():
    for length in (11, 129, 16.5, True, "20", None):
        response = client.post("/generate", json={"length": length})
        assert response.status_code == 422
