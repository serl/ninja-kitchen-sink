from rest_framework import routers, serializers, viewsets

from .models import Choice, Question

router = routers.SimpleRouter()


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["id", "choice_text", "votes"]
        read_only_fields = ["votes"]


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, default=list)

    class Meta:
        model = Question
        fields = ["id", "question_text", "pub_date", "tags", "choices"]

    def create(self, validated_data):
        choices_data = validated_data.pop("choices", [])
        instance = super().create(validated_data)
        for choice_data in choices_data:
            Choice.objects.create(question=instance, **choice_data)
        return instance

    def update(self, instance, validated_data):
        choices_data = validated_data.pop("choices", [])
        if not self.partial:
            instance.choices.all().delete()
            for choice_data in choices_data:
                Choice.objects.create(question=instance, **choice_data)
        return super().update(instance, validated_data)


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


router.register("questions", QuestionViewSet)


urlpatterns = router.urls
