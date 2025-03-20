from django.db import models
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from .validators import validate_options
from django.core.validators import MinValueValidator, MaxValueValidator
import json

User=get_user_model()

class Trait(models.Model):
    CODE_CHOICES=[
        ('O', _('Openness')),
        ('C', _('Conscientiousness')),
        ('E', _('Extraversion')),
        ('A', _('Agreeableness')),
        ('N', _('Neuroticism')),
    ]
    code=models.CharField(max_length=1, choices=CODE_CHOICES, unique=True)
    name=models.CharField(max_length=20)
    description=models.TextField()
    low_range=models.TextField(help_text='Description for scores 0-40%', blank=True)
    mid_range=models.TextField(help_text='Description for scores 40-60%', blank=True)
    high_range=models.TextField(help_text='Description for scores 60-100%', blank=True)
    reverse_scored=models.BooleanField(default=False)

    class Meta:
        verbose_name=_("Personality Trait")
        verbose_name_plural=_("Personality Traits")

    def __str__(self):
        return f"{self.get_code_display()} ֊ {self.name}"


    


class PsychoTest(models.Model):
    TEST_TYPES=[
        ('BIG5', 'Big 5 Personality'),
        ('MBTI', "Myers-Briggs Type Indicator"),
        ('HOGAN', 'Hogan Personality Inventory'),
        
    ]
    name=models.CharField(max_length=255)
    test_type=models.CharField(max_length=10, choices=TEST_TYPES)
    description=models.TextField()
    created_by=models.ForeignKey(User, on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    is_active=models.BooleanField(default=True)

    def __str__(self):
        return self.name
    

def default_option():
    return json.dumps([{"text": "Այո", "value": 1}, {"text": "Ոչ", "value": 0}])


class Question(models.Model):


    TYPE_CHOICES = [
        ('yes_no', 'YES/NO'),
        ('multiple_choice', 'Multiple Choice'),
        ('open_text', 'Open Text'),
        ('rating_scale', '1-10 Rating Scale'),
         ]
    
    test=models.ForeignKey(PsychoTest, related_name="questions", on_delete=models.CASCADE)
    title=models.CharField(max_length=255)  #question
    order=models.PositiveBigIntegerField(default=0) 
    trait=models.ForeignKey('Trait', on_delete=models.PROTECT, related_name='questions')
    key=models.CharField(max_length=1, choices=[('+', 'Positive'), ('-', 'Negative')], default='+') 

    #Max 2, min 0.5
    weight = models.FloatField(default=1.0, validators=[MinValueValidator(0.5), MaxValueValidator(2.0)]) #Importance of question
    question_type=models.CharField(choices=TYPE_CHOICES, max_length=50, default='yes_no')
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

    scale_min=models.IntegerField(
        blank=True,
        null=True,
        default=1,
        verbose_name= "Նվազագույն բալ"
    )
    scale_max=models.IntegerField(
        blank=True,
        null=True,
        default=10,
        verbose_name="Մաքսիմալ բալ"
    )

    multiple_choices=models.JSONField(
        blank=True,
        null=True,
        default=None,
        validators=[validate_options],
    #    help_text="Մուտքագրեք ընտրանքները JSON ձևաչափով, օր. [\"Տարբերակ 1\", \"Տարբերակ 2\"]"
       help_text=_("Օրինակ՝ [{'text': 'Տարբերակ 1', 'value': 1}, {'text': 'Տարբերակ 2', 'value': 2}]")
    )
    open_text_prompt=models.TextField(
        blank=True,
        null=True,
        help_text="Մուտքագրեք հարցի հրահանգները"
    )
    def clean(self):
        super().clean()
        if self.question_type == 'yes_no':
            self.multiple_choices = json.dumps([{"text": "Այո", "value": 1}, {"text": "Ոչ", "value": 0}], ensure_ascii=False)
            self.open_text_prompt = None
            self.scale_max = None
            self.scale_min = None
        
        

        if self.question_type == 'rating_scale':
            if not (1<=self.scale_min<self.scale_max<=10):
                raise ValidationError({
                    'scale_min':"Նվազագույնը պետք է լինի >= 1",
                    'scale_max': 'Առավելագույնը պետք է լինի <=10'})


        if self.question_type == 'multiple_choice' and not self.multiple_choices:
            raise ValidationError({'multiple_choices': 'Մուտքագրեք պատասխանները JSON ձևաչափով'})
        
        if self.question_type == 'open_text' and not self.open_text_prompt:
            raise ValidationError({'open_text_prompt': 'Մուտքագրեք ձեր պատասխանը'})

    def save(self, *args, **kwargs):
        # Call clean to ensure validation and field setting
        self.clean()
        super().save(*args, **kwargs)
    def get_options(self):
        if self.question_type == 'yes_no':
            return [{"text": "Այո", "value": 1}, {"text": "Ոչ", "value": 0}]
        return self.multiple_choices if self.question_type == 'multiple_choice' else []


    @staticmethod
    def validate_options(value):
        try:
            if not isinstance(value, list) or len(value) < 2:
               raise ValidationError('Should be at least 2 optiosssssssssss')
            for item in value:
                if not isinstance(item, dict):
                   raise ValidationError('Each option must be a dictionary')
                if 'text' not in item or 'value' not in item:
                   raise ValidationError(_('Each option must have text and value fields'))
                if not isinstance(item['value'], (int, float)):
                   raise ValidationError(_('Value must be a number'))
        except (TypeError, ValueError):
            raise ValidationError(_('Invalid JSON format'))
        
    class Meta:
        ordering=['order']    
        verbose_name = _("Assessment Question")
        verbose_name_plural = _("Assessment Questions")
   
    def __str__(self):
        return f"{self.title} ({self.get_question_type_display()}) "
    
    
        #super().clean()



class Answer(models.Model):
    user = models.CharField(max_length=100)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    choice = models.CharField(max_length=250)
    value=models.IntegerField()
    description=models.TextField(blank=True)
    test_date = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.user} - {self.question.title} -{self.choice}"


class TestSession(models.Model):
    candidate=models.ForeignKey(User, on_delete=models.CASCADE)
    test=models.ForeignKey(PsychoTest, on_delete=models.CASCADE)
    start_time=models.DateTimeField(auto_now_add=True)
    end_time=models.DateTimeField(null=True, blank=True)
    is_completed=models.BooleanField(default=False)
    free_response=models.TextField(blank=True, null=True)
 


    def duration(self):
        if self.end_time:
            return self.end_time-self.start_time
        return None
    

class Response(models.Model):
    session=models.ForeignKey(TestSession, related_name="responses", on_delete=models.CASCADE)
    question=models.ForeignKey(Question,related_name='question_responses', on_delete=models.CASCADE)
   # choice=models.ForeignKey(Question,related_name='choice_responses', on_delete=models.CASCADE)
    choice=models.CharField(max_length=250, blank=True, null=True)
    scale_value=models.IntegerField(blank=True, null=True)
    scenario_analysis=models.JSONField(blank=True, null=True)
    response_time=models.DateTimeField(default=now)

    class Meta:
        unique_together=('session', 'question')

    def save(self, *args, **kwargs):
        # Ensure either choice or scale_value is provided
        if not self.choice and self.scale_value is None:
            raise ValueError("Either 'choice' or 'scale_value' must be provided.")
        super().save(*args, **kwargs)




class Result(models.Model):
    session=models.OneToOneField(TestSession, on_delete=models.CASCADE)
    raw_scores = models.JSONField(default=dict, blank=True, null=True)
    normalized_scores = models.JSONField(default=dict, blank=True)
    interpretation = models.JSONField(default=dict, blank=True)
    recommendations = models.JSONField(default=dict, blank=True)
    theoretical_scores = models.JSONField(default=dict, blank=True)
    scenario_analysis = models.JSONField(default=dict)
    scale_evaluations = models.JSONField(default=dict)
    free_response_analysis = models.TextField(blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    is_archived = models.BooleanField(default=False)

    def get_sumary(self):
        return {
            'traits': self.theoretical_scores,
            'scenario_analysis': self.scenario_analysis,
            'scale_evaluations': self.scale_evaluations,
            
        }
    def get_trait_score(self, trait_code):
        return self.normalized_scores.get(trait_code, 0)


#avel  
class Resulttttt(models.Model):
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
