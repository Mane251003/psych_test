from django.contrib import admin
from .models import PsychoTest, Question, Answer, TestSession, Response, Result
import json


from django.contrib import admin
from .models import *

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ('title', 'question_type', 'trait', 'order')
    show_change_link = True

@admin.register(PsychoTest)
class PsychoTestAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ('name', 'test_type', 'created_by', 'is_active')
    search_fields = ('name', 'description')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'question_type', 'created_at')
    list_filter = ('question_type', 'created_at')
    search_fields = ('title', 'trait')
    date_hierarchy = 'created_at'

    
    fieldsets = (
        (None, {
            'fields': ('title', 'test', 'order', 'key','trait', 'weight', 'question_type')
        }),
        ('Multiple Choice Options', {
            'fields': ('multiple_choices',),
            'classes': ('collapse',),
            'description': 'Լրացրեք ընտրանքները JSON ձևաչափով'
        }),
        ('Open Text Options', {
            'fields': ('open_text_prompt',),
            'classes': ('collapse',),
            'description': 'Լրացրեք հրահանգները'
        }),
        ('Rating Scale Options', {
            'fields':('scale_min', 'scale_max'),
            'classes':('collapse',),
            'description': 'Ընտրեք բալային համակարգը'
        })
    )

    
    def get_fields(self, request, obj=None):
        
        fields = super().get_fields(request, obj)
        if obj:
            if obj.question_type == 'yes_no':
               
                fields = [f for f in fields if f not in ('open_text_prompt', 'scale_min', 'scale_max')]
            elif obj.question_type == 'multiple_choice':
                fields = [f for f in fields if f not in ('open_text_prompt', 'scale_min', 'scale_max')]
            elif obj.question_type == 'open_text':
                fields = [f for f in fields if f not in ('multiple_choices', 'scale_min', 'scale_max')]
            elif obj.question_type == 'rating_scale':
                fields = [f for f in fields if f not in ('multiple_choices', 'open_text_prompt')]

        return fields
    

    def get_readonly_fields(self, request, obj=None):
        readonly_fields=super().get_readonly_fields(request, obj)
        if obj and obj.question_type == 'yes_no':
            return list(readonly_fields)+['multiple_choices']
        return readonly_fields




    def save_model(self, request, obj, form, change):
        """Auto-populate yes/no options and validate data"""
        if obj.question_type == 'yes_no':
            
            obj.multiple_choices =json.dumps([{"text": "Այո", "value": 1}, {"text": "Ոչ", "value": 0}])
            obj.open_text_prompt = None
            obj.scale_min=None
            obj.scale_max=None
        elif obj.question_type=='multiple_choice':
            obj.open_text_prompt=None
            obj.scale_min=None
            obj.scale_max=None

        elif obj.question_type=='open_text':
            obj.multiple_choices=None
            obj.scale_min=None
            obj.scale_max=None           
        
        elif obj.question_type=='rating_scale':
            obj.multiple_choices=None
            obj.open_text_prompt=None
            
        # Validate the model instance before saving
 
        try:
            obj.full_clean()
        except ValidationError as e:
            form.add_error(None, e)
            raise

        super().save_model(request, obj, form, change)
        




    class Media:
        js = ('js/admin/question_type_handler.js',)
        



@admin.register(TestSession)
class TestSessionAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'test', 'start_time', 'is_completed')
    readonly_fields = ('start_time', 'end_time')


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display=('session', 'generated_at', 'summary')
    readonly_fields=('session', 'generated_at')

    def summary(self, obj):
        return f"Theory: {len(obj.theoretical_scores)} traits, Scales: {len(obj.scale_evaluations)}"


@admin.register(Trait)
class TraitAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'reverse_scored')
    search_fields = ('name', 'description')


admin.site.register(Response)

admin.site.register(Answer)