from django.urls import path
from rest_framework import generics, routers, serializers, viewsets

from .models import Choice, Question

router = routers.SimpleRouter()


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            "id",
            "question_text",
            "pub_date",
        ]


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


router.register("questions", QuestionViewSet)


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["id", "choice_text", "votes"]
        read_only_fields = ["votes"]


class ChoiceCreateView(generics.CreateAPIView):
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer

    def perform_create(self, serializer):
        question = generics.get_object_or_404(
            Question,
            id=self.kwargs["question_id"],
        )
        serializer.save(question=question)


urlpatterns = [
    *router.urls,
    path(
        "questions/<int:question_id>/choices/",
        ChoiceCreateView.as_view(),
        name="choice-create",
    ),
]
