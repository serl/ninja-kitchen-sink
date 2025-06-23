from datetime import datetime
from unittest.mock import ANY
from zoneinfo import ZoneInfo

from django.contrib.auth.models import Permission, User
from django.test import TestCase
from parameterized import parameterized_class

from ninja_kitchen_sink.polls.models import Choice, Question, Tag


@parameterized_class(
    ("base_api",),
    [
        ("ninja-api",),
        ("drf-api",),
    ],
)
class CreateQuestionTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tag_1 = Tag.objects.create(name="Tag1")
        cls.user = User.objects.create_user("testuser")
        cls.user.user_permissions.add(
            Permission.objects.get(codename="add_question"),
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_unauthenticated_create(self):
        self.client.logout()
        response = self.client.post(
            f"/{self.base_api}/polls-v2/questions/",
            {},
            content_type="application/json",
        )

        if self.base_api == "ninja-api":
            assert response.status_code == 401
            assert response.json() == {"detail": "Unauthorized"}
        else:
            assert response.status_code == 403
            assert response.json() == {
                "detail": "Authentication credentials were not provided."
            }

    def test_unauthorized_create(self):
        unauthorized_user = User.objects.create_user("unauthorized_user")
        self.client.force_login(unauthorized_user)

        response = self.client.post(
            f"/{self.base_api}/polls-v2/questions/",
            {},
            content_type="application/json",
        )

        if self.base_api == "ninja-api":
            assert response.status_code == 401
            assert response.json() == {"detail": "Unauthorized"}
        else:
            assert response.status_code == 403
            assert response.json() == {
                "detail": "You do not have permission to perform this action."
            }

    def test_create_success(self):
        response = self.client.post(
            f"/{self.base_api}/polls-v2/questions/",
            {
                "question_text": "Second question?",
                "pub_date": "2025-01-01T12:00:00Z",
                "tags": [self.tag_1.id],
                "choices": [
                    {
                        "choice_text": "Choice 1",
                    },
                    {
                        "choice_text": "Choice 2",
                        "votes": 123,  # Ignored
                    },
                ],
            },
            content_type="application/json",
        )
        assert response.status_code == 201
        assert response.json() == {
            "id": ANY,
            "question_text": "Second question?",
            "pub_date": "2025-01-01T12:00:00Z",
            "tags": [self.tag_1.id],
            "choices": [
                {
                    "id": ANY,
                    "choice_text": "Choice 1",
                    "votes": 0,
                },
                {
                    "id": ANY,
                    "choice_text": "Choice 2",
                    "votes": 0,
                },
            ],
        }

        new_question_id = response.json()["id"]
        new_question = Question.objects.get(id=new_question_id)
        assert new_question.question_text == "Second question?"
        assert new_question.pub_date == datetime(
            2025, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC")
        )
        assert list(new_question.tags.all()) == [self.tag_1]

    def test_create_without_choices_success(self):
        response = self.client.post(
            f"/{self.base_api}/polls-v2/questions/",
            {
                "question_text": "Second question?",
                "pub_date": "2025-01-01T12:00:00Z",
                "tags": [self.tag_1.id],
                "choices": [],
            },
            content_type="application/json",
        )
        assert response.status_code == 201
        assert response.json() == {
            "id": ANY,
            "question_text": "Second question?",
            "pub_date": "2025-01-01T12:00:00Z",
            "tags": [self.tag_1.id],
            "choices": [],
        }

        new_question_id = response.json()["id"]
        new_question = Question.objects.get(id=new_question_id)
        assert new_question.question_text == "Second question?"
        assert new_question.pub_date == datetime(
            2025, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC")
        )
        assert list(new_question.tags.all()) == [self.tag_1]

    def test_missing_fields(self):
        response = self.client.post(
            f"/{self.base_api}/polls-v2/questions/",
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
            f"/{self.base_api}/polls-v2/questions/",
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

    def test_invalid_tag(self):
        response = self.client.post(
            f"/{self.base_api}/polls-v2/questions/",
            {
                "question_text": "Fifth question?",
                "pub_date": "2025-01-01T12:00:00Z",
                "tags": [self.tag_1.id + 1],
            },
            content_type="application/json",
        )

        if self.base_api == "ninja-api":
            assert response.status_code == 422
            assert response.json() == {
                "detail": [
                    {"tags": f"Tags with IDs {{{self.tag_1.id + 1}}} do not exist."},
                ]
            }
        else:
            assert response.status_code == 400
            assert response.json() == {
                "tags": [f'Invalid pk "{self.tag_1.id + 1}" - object does not exist.']
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
        cls.tag_1 = Tag.objects.create(name="Tag1")
        cls.question_1 = Question.objects.create(
            question_text="First question?",
            pub_date=datetime(2025, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC")),
        )
        cls.question_1.tags.set([cls.tag_1])
        cls.question_2 = Question.objects.create(
            question_text="Second question?",
            pub_date=datetime(2025, 2, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC")),
        )
        Choice.objects.create(
            question=cls.question_2,
            choice_text="Choice 1",
        )
        Choice.objects.create(
            question=cls.question_2,
            choice_text="Choice 2",
            votes=3,
        )
        cls.user = User.objects.create_user("testuser")

    def setUp(self):
        self.client.force_login(self.user)

    def test_unauthenticated_list(self):
        self.client.logout()
        response = self.client.get(
            f"/{self.base_api}/polls-v2/questions/",
        )

        if self.base_api == "ninja-api":
            assert response.status_code == 401
            assert response.json() == {"detail": "Unauthorized"}
        else:
            assert response.status_code == 403
            assert response.json() == {
                "detail": "Authentication credentials were not provided."
            }

    def test_list_questions(self):
        response = self.client.get(
            f"/{self.base_api}/polls-v2/questions/",
        )
        assert response.status_code == 200
        assert len(response.json()) == 2
        assert response.json()[0] == {
            "id": self.question_1.id,
            "question_text": "First question?",
            "pub_date": "2025-01-01T12:00:00Z",
            "tags": [self.tag_1.id],
            "choices": [],
        }
        assert response.json()[1] == {
            "id": self.question_2.id,
            "question_text": "Second question?",
            "pub_date": "2025-02-01T12:00:00Z",
            "tags": [],
            "choices": [
                {
                    "id": ANY,
                    "choice_text": "Choice 1",
                    "votes": 0,
                },
                {
                    "id": ANY,
                    "choice_text": "Choice 2",
                    "votes": 3,
                },
            ],
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
        cls.tag_1 = Tag.objects.create(name="Tag1")
        cls.question = Question.objects.create(
            question_text="First question?",
            pub_date=datetime(2025, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC")),
        )
        cls.question.tags.set([cls.tag_1])
        cls.user = User.objects.create_user("testuser")

    def setUp(self):
        self.client.force_login(self.user)

    def test_unauthenticated_get(self):
        self.client.logout()
        response = self.client.get(
            f"/{self.base_api}/polls-v2/questions/{self.question.id}/",
        )

        if self.base_api == "ninja-api":
            assert response.status_code == 401
            assert response.json() == {"detail": "Unauthorized"}
        else:
            assert response.status_code == 403
            assert response.json() == {
                "detail": "Authentication credentials were not provided."
            }

    def test_get_question(self):
        response = self.client.get(
            f"/{self.base_api}/polls-v2/questions/{self.question.id}/",
        )
        assert response.status_code == 200
        assert response.json() == {
            "id": self.question.id,
            "question_text": "First question?",
            "pub_date": "2025-01-01T12:00:00Z",
            "tags": [self.tag_1.id],
            "choices": [],
        }

    def test_get_nonexistent_question(self):
        response = self.client.get(
            f"/{self.base_api}/polls-v2/questions/{self.question.id + 1}/",
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
class UpdateQuestionTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tag_1 = Tag.objects.create(name="Tag1")
        cls.tag_2 = Tag.objects.create(name="Tag2")
        cls.question = Question.objects.create(
            question_text="First question?",
            pub_date=datetime(2025, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC")),
        )
        cls.question.tags.set([cls.tag_1])

        Choice.objects.create(
            question=cls.question,
            choice_text="Choice 1",
        )
        Choice.objects.create(
            question=cls.question,
            choice_text="Choice 2",
            votes=3,
        )
        cls.user = User.objects.create_user("testuser")
        cls.user.user_permissions.add(
            Permission.objects.get(codename="change_question"),
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_unauthenticated_update(self):
        self.client.logout()
        response = self.client.put(
            f"/{self.base_api}/polls-v2/questions/{self.question.id}/",
            {},
            content_type="application/json",
        )

        if self.base_api == "ninja-api":
            assert response.status_code == 401
            assert response.json() == {"detail": "Unauthorized"}
        else:
            assert response.status_code == 403
            assert response.json() == {
                "detail": "Authentication credentials were not provided."
            }

    def test_unauthorized_update(self):
        unauthorized_user = User.objects.create_user("unauthorized_user")
        self.client.force_login(unauthorized_user)

        response = self.client.put(
            f"/{self.base_api}/polls-v2/questions/{self.question.id}/",
            {},
            content_type="application/json",
        )

        if self.base_api == "ninja-api":
            assert response.status_code == 401
            assert response.json() == {"detail": "Unauthorized"}
        else:
            assert response.status_code == 403
            assert response.json() == {
                "detail": "You do not have permission to perform this action."
            }

    def test_update_question(self):
        response = self.client.put(
            f"/{self.base_api}/polls-v2/questions/{self.question.id}/",
            {
                "question_text": "Updated question?",
                "pub_date": "2025-02-01T12:00:00Z",
                "tags": [self.tag_2.id],
                "choices": [
                    {
                        "choice_text": "Choice 3",
                    },
                    {
                        "choice_text": "Choice 4",
                    },
                ],
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json() == {
            "id": self.question.id,
            "question_text": "Updated question?",
            "pub_date": "2025-02-01T12:00:00Z",
            "tags": [self.tag_2.id],
            "choices": [
                {
                    "id": ANY,
                    "choice_text": "Choice 3",
                    "votes": 0,
                },
                {
                    "id": ANY,
                    "choice_text": "Choice 4",
                    "votes": 0,
                },
            ],
        }

        updated_question = Question.objects.get(id=self.question.id)
        assert updated_question.question_text == "Updated question?"
        assert updated_question.pub_date == datetime(
            2025, 2, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC")
        )
        assert list(updated_question.tags.all()) == [self.tag_2]

    def test_update_missing_fields(self):
        response = self.client.put(
            f"/{self.base_api}/polls-v2/questions/{self.question.id}/",
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
            f"/{self.base_api}/polls-v2/questions/{self.question.id + 1}/",
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

    def test_update_invalid_tag(self):
        response = self.client.put(
            f"/{self.base_api}/polls-v2/questions/{self.question.id}/",
            {
                "question_text": "Updated question?",
                "pub_date": "2025-02-01T12:00:00Z",
                "tags": [self.tag_2.id + 1],
            },
            content_type="application/json",
        )

        if self.base_api == "ninja-api":
            assert response.status_code == 422
            assert response.json() == {
                "detail": [
                    {"tags": f"Tags with IDs {{{self.tag_2.id + 1}}} do not exist."},
                ]
            }
        else:
            assert response.status_code == 400
            assert response.json() == {
                "tags": [f'Invalid pk "{self.tag_2.id + 1}" - object does not exist.']
            }


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
        cls.tag_1 = Tag.objects.create(name="Tag1")
        cls.tag_2 = Tag.objects.create(name="Tag2")
        cls.question = Question.objects.create(
            question_text="First question?",
            pub_date=datetime(2025, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC")),
        )
        cls.question.tags.set([cls.tag_1])

        Choice.objects.create(
            question=cls.question,
            choice_text="Choice 1",
        )
        Choice.objects.create(
            question=cls.question,
            choice_text="Choice 2",
            votes=3,
        )
        cls.user = User.objects.create_user("testuser")
        cls.user.user_permissions.add(
            Permission.objects.get(codename="change_question"),
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_unauthenticated_partial_update(self):
        self.client.logout()
        response = self.client.patch(
            f"/{self.base_api}/polls-v2/questions/{self.question.id}/",
            {},
            content_type="application/json",
        )

        if self.base_api == "ninja-api":
            assert response.status_code == 401
            assert response.json() == {"detail": "Unauthorized"}
        else:
            assert response.status_code == 403
            assert response.json() == {
                "detail": "Authentication credentials were not provided."
            }

    def test_unauthorized_partial_update(self):
        unauthorized_user = User.objects.create_user("unauthorized_user")
        self.client.force_login(unauthorized_user)

        response = self.client.patch(
            f"/{self.base_api}/polls-v2/questions/{self.question.id}/",
            {},
            content_type="application/json",
        )

        if self.base_api == "ninja-api":
            assert response.status_code == 401
            assert response.json() == {"detail": "Unauthorized"}
        else:
            assert response.status_code == 403
            assert response.json() == {
                "detail": "You do not have permission to perform this action."
            }

    def test_partial_update_question(self):
        response = self.client.patch(
            f"/{self.base_api}/polls-v2/questions/{self.question.id}/",
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
            "tags": [self.tag_1.id],
            "choices": [
                {
                    "id": ANY,
                    "choice_text": "Choice 1",
                    "votes": 0,
                },
                {
                    "id": ANY,
                    "choice_text": "Choice 2",
                    "votes": 3,
                },
            ],
        }

        updated_question = Question.objects.get(id=self.question.id)
        assert updated_question.question_text == "Partially updated question?"
        assert updated_question.pub_date == datetime(
            2025, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC")
        )
        assert list(updated_question.tags.all()) == [self.tag_1]

    def test_update_tag(self):
        response = self.client.patch(
            f"/{self.base_api}/polls-v2/questions/{self.question.id}/",
            {
                "tags": [self.tag_2.id],
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json() == {
            "id": self.question.id,
            "question_text": "First question?",
            "pub_date": "2025-01-01T12:00:00Z",
            "tags": [self.tag_2.id],
            "choices": [
                {
                    "id": ANY,
                    "choice_text": "Choice 1",
                    "votes": 0,
                },
                {
                    "id": ANY,
                    "choice_text": "Choice 2",
                    "votes": 3,
                },
            ],
        }

        updated_question = Question.objects.get(id=self.question.id)
        assert updated_question.question_text == "First question?"
        assert updated_question.pub_date == datetime(
            2025, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC")
        )
        assert list(updated_question.tags.all()) == [self.tag_2]

    def test_ignore_choices_on_partial_update(self):
        response = self.client.patch(
            f"/{self.base_api}/polls-v2/questions/{self.question.id}/",
            {
                "choices": [
                    {
                        "choice_text": "Choice 3",
                    },
                    {
                        "choice_text": "Choice 4",
                    },
                ],
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json() == {
            "id": self.question.id,
            "question_text": "First question?",
            "pub_date": "2025-01-01T12:00:00Z",
            "tags": [self.tag_1.id],
            "choices": [
                {
                    "id": ANY,
                    "choice_text": "Choice 1",
                    "votes": 0,
                },
                {
                    "id": ANY,
                    "choice_text": "Choice 2",
                    "votes": 3,
                },
            ],
        }

        updated_question = Question.objects.get(id=self.question.id)
        assert updated_question.question_text == "First question?"
        assert updated_question.pub_date == datetime(
            2025, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC")
        )
        assert list(updated_question.tags.all()) == [self.tag_1]

    def test_update_nonexistent_question(self):
        response = self.client.patch(
            f"/{self.base_api}/polls-v2/questions/{self.question.id + 1}/",
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

    def test_update_invalid_tag(self):
        response = self.client.patch(
            f"/{self.base_api}/polls-v2/questions/{self.question.id}/",
            {
                "tags": [self.tag_2.id + 1],
            },
            content_type="application/json",
        )

        if self.base_api == "ninja-api":
            assert response.status_code == 422
            assert response.json() == {
                "detail": [
                    {"tags": f"Tags with IDs {{{self.tag_2.id + 1}}} do not exist."},
                ]
            }
        else:
            assert response.status_code == 400
            assert response.json() == {
                "tags": [f'Invalid pk "{self.tag_2.id + 1}" - object does not exist.']
            }


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
        Choice.objects.create(
            question=cls.question,
            choice_text="Choice 1",
        )
        Choice.objects.create(
            question=cls.question,
            choice_text="Choice 2",
            votes=3,
        )
        cls.user = User.objects.create_user("testuser")
        cls.user.user_permissions.add(
            Permission.objects.get(codename="delete_question"),
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_unauthenticated_delete(self):
        self.client.logout()
        response = self.client.delete(
            f"/{self.base_api}/polls-v2/questions/{self.question.id}/",
        )

        if self.base_api == "ninja-api":
            assert response.status_code == 401
            assert response.json() == {"detail": "Unauthorized"}
        else:
            assert response.status_code == 403
            assert response.json() == {
                "detail": "Authentication credentials were not provided."
            }

    def test_unauthorized_delete(self):
        unauthorized_user = User.objects.create_user("unauthorized_user")
        self.client.force_login(unauthorized_user)

        response = self.client.delete(
            f"/{self.base_api}/polls-v2/questions/{self.question.id}/",
        )

        if self.base_api == "ninja-api":
            assert response.status_code == 401
            assert response.json() == {"detail": "Unauthorized"}
        else:
            assert response.status_code == 403
            assert response.json() == {
                "detail": "You do not have permission to perform this action."
            }

    def test_delete_question(self):
        response = self.client.delete(
            f"/{self.base_api}/polls-v2/questions/{self.question.id}/",
        )
        assert response.status_code == 204

        with self.assertRaises(Question.DoesNotExist):
            Question.objects.get(id=self.question.id)

        assert Question.objects.count() == 0
        assert Choice.objects.count() == 0

    def test_delete_nonexistent_question(self):
        response = self.client.delete(
            f"/{self.base_api}/polls-v2/questions/{self.question.id + 1}/",
        )

        assert response.status_code == 404

        if self.base_api == "ninja-api":
            assert response.json() == {"detail": "Not Found"}
        else:
            assert response.json() == {"detail": "No Question matches the given query."}
