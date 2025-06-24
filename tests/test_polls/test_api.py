from datetime import datetime
from unittest.mock import ANY
from zoneinfo import ZoneInfo

from django.test import TestCase
from parameterized import parameterized_class

from ninja_kitchen_sink.polls.models import Question


@parameterized_class(
    ("base_api",),
    [
        ("ninja-api",),
        ("drf-api",),
    ],
)
class CreateQuestionTestCase(TestCase):
    def test_create_success(self):
        response = self.client.post(
            f"/{self.base_api}/polls/questions/",
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
            f"/{self.base_api}/polls/questions/",
            {
                "question_text": "Third question?",
            },
            content_type="application/json",
        )

        if self.base_api == "ninja-api":
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
        else:
            assert response.status_code == 400
            assert response.json() == {
                "pub_date": ["This field is required."],
            }

    def test_invalid_date_format(self):
        response = self.client.post(
            f"/{self.base_api}/polls/questions/",
            {
                "question_text": "Fourth question?",
                "pub_date": "invalid-date-format",
            },
            content_type="application/json",
        )

        if self.base_api == "ninja-api":
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
        else:
            assert response.status_code == 400
            assert response.json() == {
                "pub_date": [
                    "Datetime has wrong format. Use one of these formats instead: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z]."
                ]
            }


@parameterized_class(
    ("base_api",),
    [
        ("ninja-api",),
        ("drf-api",),
    ],
)
class ListQuestionTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.question = Question.objects.create(
            question_text="First question?",
            pub_date=datetime(2025, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC")),
        )

    def test_list_questions(self):
        response = self.client.get(
            f"/{self.base_api}/polls/questions/",
        )
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0] == {
            "id": self.question.id,
            "question_text": "First question?",
            "pub_date": "2025-01-01T12:00:00Z",
        }


@parameterized_class(
    ("base_api",),
    [
        ("ninja-api",),
        ("drf-api",),
    ],
)
class GetQuestionTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.question = Question.objects.create(
            question_text="First question?",
            pub_date=datetime(2025, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC")),
        )

    def test_get_question(self):
        response = self.client.get(
            f"/{self.base_api}/polls/questions/{self.question.id}/",
        )
        assert response.status_code == 200
        assert response.json() == {
            "id": self.question.id,
            "question_text": "First question?",
            "pub_date": "2025-01-01T12:00:00Z",
        }

    def test_get_nonexistent_question(self):
        response = self.client.get(
            f"/{self.base_api}/polls/questions/{self.question.id + 1}/",
        )

        assert response.status_code == 404

        if self.base_api == "ninja-api":
            assert response.json() == {"detail": "Not Found"}
        else:
            assert response.json() == {"detail": "No Question matches the given query."}


class AsyncGetQuestionTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.question = Question.objects.create(
            question_text="First question?",
            pub_date=datetime(2025, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC")),
        )

    def test_get_question(self):
        response = self.client.get(
            f"/ninja-api/polls-async/questions/{self.question.id}/",
        )
        assert response.status_code == 200
        assert response.json() == {
            "id": self.question.id,
            "question_text": "First question?",
            "pub_date": "2025-01-01T12:00:00Z",
        }

    def test_get_nonexistent_question(self):
        response = self.client.get(
            f"/ninja-api/polls-async/questions/{self.question.id + 1}/",
        )

        assert response.status_code == 404

        assert response.json() == {"detail": "Not Found"}


@parameterized_class(
    ("base_api",),
    [
        ("ninja-api",),
        ("drf-api",),
    ],
)
class UpdateQuestionTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.question = Question.objects.create(
            question_text="First question?",
            pub_date=datetime(2025, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC")),
        )

    def test_update_question(self):
        response = self.client.put(
            f"/{self.base_api}/polls/questions/{self.question.id}/",
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
            f"/{self.base_api}/polls/questions/{self.question.id}/",
            {
                "question_text": "Updated question?",
            },
            content_type="application/json",
        )

        if self.base_api == "ninja-api":
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
        else:
            assert response.status_code == 400
            assert response.json() == {
                "pub_date": ["This field is required."],
            }

    def test_update_nonexistent_question(self):
        response = self.client.put(
            f"/{self.base_api}/polls/questions/{self.question.id + 1}/",
            {
                "question_text": "Nonexistent question?",
                "pub_date": "2025-02-01T12:00:00Z",
            },
            content_type="application/json",
        )

        assert response.status_code == 404

        if self.base_api == "ninja-api":
            assert response.json() == {"detail": "Not Found"}
        else:
            assert response.json() == {"detail": "No Question matches the given query."}


@parameterized_class(
    ("base_api",),
    [
        ("ninja-api",),
        ("drf-api",),
    ],
)
class PartialUpdateQuestionTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.question = Question.objects.create(
            question_text="First question?",
            pub_date=datetime(2025, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC")),
        )

    def test_partial_update_question(self):
        response = self.client.patch(
            f"/{self.base_api}/polls/questions/{self.question.id}/",
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
            f"/{self.base_api}/polls/questions/{self.question.id + 1}/",
            {
                "question_text": "Nonexistent question?",
            },
            content_type="application/json",
        )

        assert response.status_code == 404

        if self.base_api == "ninja-api":
            assert response.json() == {"detail": "Not Found"}
        else:
            assert response.json() == {"detail": "No Question matches the given query."}


@parameterized_class(
    ("base_api",),
    [
        ("ninja-api",),
        ("drf-api",),
    ],
)
class DeleteQuestionTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.question = Question.objects.create(
            question_text="First question?",
            pub_date=datetime(2025, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC")),
        )

    def test_delete_question(self):
        response = self.client.delete(
            f"/{self.base_api}/polls/questions/{self.question.id}/",
        )
        assert response.status_code == 204

        with self.assertRaises(Question.DoesNotExist):
            Question.objects.get(id=self.question.id)

    def test_delete_nonexistent_question(self):
        response = self.client.delete(
            f"/{self.base_api}/polls/questions/{self.question.id + 1}/",
        )

        assert response.status_code == 404

        if self.base_api == "ninja-api":
            assert response.json() == {"detail": "Not Found"}
        else:
            assert response.json() == {"detail": "No Question matches the given query."}


@parameterized_class(
    ("base_api",),
    [
        ("ninja-api",),
        ("drf-api",),
    ],
)
class AddChoiceTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.question = Question.objects.create(
            question_text="First question?",
            pub_date=datetime(2025, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC")),
        )

    def test_add_choice(self):
        response = self.client.post(
            f"/{self.base_api}/polls/questions/{self.question.id}/choices/",
            {
                "choice_text": "Choice A",
            },
            content_type="application/json",
        )
        assert response.status_code == 201
        assert response.json() == {
            "id": ANY,
            "choice_text": "Choice A",
            "votes": 0,
        }

    def test_ignore_votes_on_create(self):
        response = self.client.post(
            f"/{self.base_api}/polls/questions/{self.question.id}/choices/",
            {
                "choice_text": "Choice A",
                "votes": 10,
            },
            content_type="application/json",
        )
        assert response.status_code == 201
        assert response.json() == {
            "id": ANY,
            "choice_text": "Choice A",
            "votes": 0,
        }

    def test_missing_choice_text(self):
        response = self.client.post(
            f"/{self.base_api}/polls/questions/{self.question.id}/choices/",
            {},
            content_type="application/json",
        )

        if self.base_api == "ninja-api":
            assert response.status_code == 422
            assert response.json() == {
                "detail": [
                    {
                        "loc": ["body", "payload", "choice_text"],
                        "msg": "Field required",
                        "type": "missing",
                    }
                ]
            }
        else:
            assert response.status_code == 400
            assert response.json() == {
                "choice_text": ["This field is required."],
            }

    def test_add_choice_to_nonexistent_question(self):
        response = self.client.post(
            f"/{self.base_api}/polls/questions/{self.question.id + 1}/choices/",
            {
                "choice_text": "Choice B",
            },
            content_type="application/json",
        )

        assert response.status_code == 404

        if self.base_api == "ninja-api":
            assert response.json() == {"detail": "Not Found"}
        else:
            assert response.json() == {"detail": "No Question matches the given query."}
