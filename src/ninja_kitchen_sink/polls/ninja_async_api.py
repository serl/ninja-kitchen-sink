from django.shortcuts import aget_object_or_404
from ninja import Router

from ninja_kitchen_sink.polls.ninja_api import QuestionOut

from .models import Question

router = Router()


@router.get("/questions/{question_id}/", response=QuestionOut)
async def get_question(request, question_id: int):
    question = await aget_object_or_404(Question, id=question_id)
    return question
