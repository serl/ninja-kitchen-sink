from django.shortcuts import get_object_or_404
from ninja import ModelSchema, PatchDict, Router
from ninja.errors import ValidationError

from .models import Choice, Question, Tag

router = Router()


class ChoiceIn(ModelSchema):
    class Meta:
        model = Choice
        fields = ["choice_text"]


class QuestionIn(ModelSchema):
    tags: list[int] | None = None
    choices: list[ChoiceIn] = []

    class Meta:
        model = Question
        fields = [
            "question_text",
            "pub_date",
            # "tags",  # This would make it required even if we have blank=True in the model
        ]


class ChoiceOut(ModelSchema):
    class Meta:
        model = Choice
        fields = ["id", "choice_text", "votes"]


class QuestionOut(ModelSchema):
    choices: list[ChoiceOut]

    class Meta:
        model = Question
        fields = [
            "id",
            "question_text",
            "pub_date",
            "tags",
            # "choices",  # "Does not exist"
        ]


@router.post("/questions/", response={201: QuestionOut})
def create_question(request, payload: QuestionIn):
    data = payload.dict()
    choices_data = data.pop("choices", [])

    tags = data.pop("tags", [])
    existing_tags = set(Tag.objects.filter(id__in=tags).values_list("id", flat=True))
    if missing_tags := set(tags) - existing_tags:
        raise ValidationError([{"tags": f"Tags with IDs {missing_tags} do not exist."}])

    question = Question.objects.create(**data)
    question.tags.set(tags)
    for choice_data in choices_data:
        Choice.objects.create(question=question, **choice_data)

    return 201, question


@router.get("/questions/", response=list[QuestionOut])
def list_questions(request):
    return Question.objects.all()


@router.get("/questions/{question_id}/", response=QuestionOut)
def get_question(request, question_id: int):
    question = get_object_or_404(Question, id=question_id)
    return question


@router.put("/questions/{question_id}/", response=QuestionOut)
def update_question(request, question_id: int, payload: QuestionIn):
    question = get_object_or_404(Question, id=question_id)
    data = payload.dict()
    choices_data = data.pop("choices", [])

    tags = data.pop("tags", [])
    existing_tags = set(Tag.objects.filter(id__in=tags).values_list("id", flat=True))
    if missing_tags := set(tags) - existing_tags:
        raise ValidationError([{"tags": f"Tags with IDs {missing_tags} do not exist."}])

    for attr, value in data.items():
        setattr(question, attr, value)
    question.save()
    question.tags.set(tags)

    question.choices.all().delete()
    for choice_data in choices_data:
        Choice.objects.create(question=question, **choice_data)

    return question


@router.patch("/questions/{question_id}/", response=QuestionOut)
def partial_update_question(request, question_id: int, payload: PatchDict[QuestionIn]):
    question = get_object_or_404(Question, id=question_id)
    payload.pop("choices", None)  # Choices are not allowed in PATCH
    tags = payload.pop("tags", None)
    if tags is not None:
        existing_tags = set(
            Tag.objects.filter(id__in=tags).values_list("id", flat=True)
        )
        if missing_tags := set(tags) - existing_tags:
            raise ValidationError(
                [{"tags": f"Tags with IDs {missing_tags} do not exist."}]
            )
        question.tags.set(tags)

    for attr, value in payload.items():
        # NOTE: payload it's a dict and not a QuestionIn, because it's wrapped in PatchDict (necessary to mark all fields as optional)
        setattr(question, attr, value)
    question.save()
    return question


@router.delete("/questions/{question_id}/", response={204: None})
def delete_question(request, question_id: int):
    question = get_object_or_404(Question, id=question_id)
    question.delete()
    return 204, None
