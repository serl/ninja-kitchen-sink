from datetime import datetime
from unittest.mock import ANY
from zoneinfo import ZoneInfo

from django.test import TestCase

from ninja_kitchen_sink.polls.models import Question


class CreateQuestionTestCase(TestCase):
    def test_create_success(self):
        response = self.client.post(
            "/api/polls/questions",
            {
                "question_text": "Second question?",
                "pub_date": "2025-01-01T12:00:00Z",
            },
            content_type="application/json",
        )
        assert response.status_code == 201
        assert response.json() == {
            "id": ANY,
            "question_text": "Second question?",
            "pub_date": "2025-01-01T12:00:00Z",
        }

        new_question_id = response.json()["id"]
        new_question = Question.objects.get(id=new_question_id)
        assert new_question.question_text == "Second question?"
        assert new_question.pub_date == datetime(
            2025, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC")
        )

    def test_missing_fields(self):
        response = self.client.post(
            "/api/polls/questions",
            {
                "question_text": "Third question?",
            },
            content_type="application/json",
        )
        assert response.status_code == 422
        assert response.json() == {
            "detail": [
                {
                    "loc": ["body", "payload", "pub_date"],
                    "msg": "Field required",
                    "type": "missing",
                }
            ]
        }

    def test_invalid_date_format(self):
        response = self.client.post(
            "/api/polls/questions",
            {
                "question_text": "Fourth question?",
                "pub_date": "invalid-date-format",
            },
            content_type="application/json",
        )
        assert response.status_code == 422
        assert response.json() == {
            "detail": [
                {
                    "ctx": {"error": "invalid character in year"},
                    "loc": ["body", "payload", "pub_date"],
                    "msg": "Input should be a valid datetime or date, invalid character in year",
                    "type": "datetime_from_date_parsing",
                }
            ]
        }


class ListQuestionTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.question = Question.objects.create(
            question_text="First question?",
            pub_date=datetime(2025, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC")),
        )

    def test_list_questions(self):
        response = self.client.get("/api/polls/questions")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0] == {
            "id": self.question.id,
            "question_text": "First question?",
            "pub_date": "2025-01-01T12:00:00Z",
        }


class GetQuestionTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.question = Question.objects.create(
            question_text="First question?",
            pub_date=datetime(2025, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC")),
        )

    def test_get_question(self):
        response = self.client.get(f"/api/polls/questions/{self.question.id}")
        assert response.status_code == 200
        assert response.json() == {
            "id": self.question.id,
            "question_text": "First question?",
            "pub_date": "2025-01-01T12:00:00Z",
        }

    def test_get_nonexistent_question(self):
        response = self.client.get(f"/api/polls/questions/{self.question.id + 1}")
        assert response.status_code == 404
        assert response.json() == {"detail": "Not Found"}


class UpdateQuestionTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.question = Question.objects.create(
            question_text="First question?",
            pub_date=datetime(2025, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC")),
        )

    def test_update_question(self):
        response = self.client.put(
            f"/api/polls/questions/{self.question.id}",
            {
                "question_text": "Updated question?",
                "pub_date": "2025-02-01T12:00:00Z",
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json() == {
            "id": self.question.id,
            "question_text": "Updated question?",
            "pub_date": "2025-02-01T12:00:00Z",
        }

        updated_question = Question.objects.get(id=self.question.id)
        assert updated_question.question_text == "Updated question?"
        assert updated_question.pub_date == datetime(
            2025, 2, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC")
        )

    def test_update_missing_fields(self):
        response = self.client.put(
            f"/api/polls/questions/{self.question.id}",
            {
                "question_text": "Updated question?",
            },
            content_type="application/json",
        )
        assert response.status_code == 422
        assert response.json() == {
            "detail": [
                {
                    "loc": ["body", "payload", "pub_date"],
                    "msg": "Field required",
                    "type": "missing",
                }
            ]
        }

    def test_update_nonexistent_question(self):
        response = self.client.put(
            f"/api/polls/questions/{self.question.id + 1}",
            {
                "question_text": "Nonexistent question?",
                "pub_date": "2025-02-01T12:00:00Z",
            },
            content_type="application/json",
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "Not Found"}


class PartialUpdateQuestionTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.question = Question.objects.create(
            question_text="First question?",
            pub_date=datetime(2025, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC")),
        )

    def test_partial_update_question(self):
        response = self.client.patch(
            f"/api/polls/questions/{self.question.id}",
            {
                "question_text": "Partially updated question?",
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json() == {
            "id": self.question.id,
            "question_text": "Partially updated question?",
            "pub_date": "2025-01-01T12:00:00Z",
        }

        updated_question = Question.objects.get(id=self.question.id)
        assert updated_question.question_text == "Partially updated question?"
        assert updated_question.pub_date == datetime(
            2025, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC")
        )

    def test_update_nonexistent_question(self):
        response = self.client.patch(
            f"/api/polls/questions/{self.question.id + 1}",
            {
                "question_text": "Nonexistent question?",
            },
            content_type="application/json",
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "Not Found"}


class DeleteQuestionTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.question = Question.objects.create(
            question_text="First question?",
            pub_date=datetime(2025, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC")),
        )

    def test_delete_question(self):
        response = self.client.delete(f"/api/polls/questions/{self.question.id}")
        assert response.status_code == 204

        with self.assertRaises(Question.DoesNotExist):
            Question.objects.get(id=self.question.id)

    def test_delete_nonexistent_question(self):
        response = self.client.delete(f"/api/polls/questions/{self.question.id + 1}")
        assert response.status_code == 404
        assert response.json() == {"detail": "Not Found"}
