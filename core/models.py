from django.db import models
from django.utils.timezone import now

def default_option():
    return ['Այո',  'Ոչ']


class Question(models.Model):
    SCALE_CHOICES = [
        ('neuroticism', 'Neuroticism'),
        ('extroversion', 'Extroversion'),
        ('psychoticism', 'Psychoticism'),
        ('sincerity', 'Sincerity')]
    
    TYPE_CHOICES = [
        ('yes_no', 'YES/NO'),
        ('multiple_choice', 'Multiple Choice'),
        ('open_text', 'Open Text')]
    title=models.CharField(max_length=255)
    question_type=models.CharField(choices=TYPE_CHOICES, max_length=50, default='yes_no')
    scale=models.CharField(max_length=50, choices=SCALE_CHOICES)
    options=models.JSONField(default=default_option, null=True, blank=True)

    def __str__(self):
        return self.title


class Answer(models.Model):
    user = models.CharField(max_length=100)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.CharField(max_length=250)
    test_date = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.user} - {self.question.title}"


class Result(models.Model):
    user = models.CharField(max_length=100)
    neuroticism_score = models.FloatField(default=0)
    neuroticism_yes = models.FloatField(default=0)
    neuroticism_no = models.FloatField(default=0)
    extroversion_score = models.FloatField(default=0)
    extroversion_yes = models.FloatField(default=0)
    extroversion_no = models.FloatField(default=0)
    psychoticism_score = models.FloatField(default=0)
    psychoticism_yes = models.FloatField(default=0)
    psychoticism_no = models.FloatField(default=0)
    sincerity_score = models.FloatField(default=0)
    sincerity_yes = models.FloatField(default=0)
    sincerity_no = models.FloatField(default=0)

    def __str__(self):
        return f"Result for {self.user}"
