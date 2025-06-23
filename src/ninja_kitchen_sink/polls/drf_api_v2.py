from rest_framework import routers, serializers, viewsets

from .models import Question

router = routers.SimpleRouter()


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            "id",
            "question_text",
            "pub_date",
            "tags",
        ]


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


router.register("questions", QuestionViewSet)


urlpatterns = router.urls
