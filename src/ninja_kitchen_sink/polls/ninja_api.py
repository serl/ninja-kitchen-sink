from django.shortcuts import get_object_or_404
from ninja import ModelSchema, PatchDict, Router

from .models import Question

router = Router()


class QuestionIn(ModelSchema):
    class Meta:
        model = Question
        fields = [
            "question_text",
            "pub_date",
        ]


class QuestionOut(ModelSchema):
    class Meta:
        model = Question
        fields = [
            "id",
            "question_text",
            "pub_date",
        ]


@router.post("/questions/", response={201: QuestionOut})
def create_question(request, payload: QuestionIn):
    question = Question.objects.create(**payload.dict())
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
    for attr, value in payload.dict().items():
        setattr(question, attr, value)
    question.save()
    return question


@router.patch("/questions/{question_id}/", response=QuestionOut)
def partial_update_question(request, question_id: int, payload: PatchDict[QuestionIn]):
    question = get_object_or_404(Question, id=question_id)
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
