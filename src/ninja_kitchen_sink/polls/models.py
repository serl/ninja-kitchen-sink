from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")
    tags = models.ManyToManyField(Tag, related_name="questions", blank=True)


class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="choices",
    )
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
