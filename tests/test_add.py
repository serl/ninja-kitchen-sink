from django.test import TestCase


class AddTestCase(TestCase):
    def test_add(self):
        response = self.client.get("/api/add", {"a": 3, "b": 5})
        assert response.status_code == 200
        assert response.json() == {"result": 8}

    def test_add_invalid_input(self):
        response = self.client.get("/api/add", {"a": "invalid", "b": 5})
        assert response.status_code == 422
        assert response.json() == {
            "detail": [
                {
                    "loc": ["query", "a"],
                    "msg": "Input should be a valid integer, unable to parse string as an integer",
                    "type": "int_parsing",
                }
            ]
        }

    def test_add_missing_parameter(self):
        response = self.client.get("/api/add", {"a": 3})
        assert response.status_code == 422
        assert response.json() == {
            "detail": [
                {
                    "loc": ["query", "b"],
                    "msg": "Field required",
                    "type": "missing",
                }
            ]
        }
