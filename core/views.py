from django.shortcuts import render, redirect, HttpResponse
from .models import Question, Answer, Result
from django.utils.timezone import now

from django.db.models import Max
from .forms import AnswerForm

from .utils.gemini import get_gemini_response
import openai
from openai import OpenAI



def take_test(request):
    questions=Question.objects.all()
    if request.method=='POST':
        test_date=now()
        for question in questions:
            choice=request.POST.get(str(question.id))
            Answer.objects.create(
                user=request.user.username,
                question=question,
                choice=choice,
                test_date=test_date
            )
        return redirect('result')
    return render(request, 'core/test.html', {'questions': questions})

def resultt(request):
    scores=Answer.objects.filter(user=request.user.username).first()
    print(scores)
    if not scores:
        return render(request, 'core/result.html', {'error':'you did not pass the test'})
    return render(request, 'core/result.html', {'scores':scores})


def result(request):
    latest_test=Answer.objects.filter(user=request.user.username).aggregate(latest_date=Max('test_date'))['latest_date']
    print(latest_test)
    user_answers=Answer.objects.filter(user=request.user.username, test_date=latest_test)
 

    scores={'neuroticism_score':0,
            "neuroticism_yes":0,
            "neuroticism_no":0,
            'extroversion_score':0,
            'extroversion_yes':0,
            'extroversion_no':0,
            "psychoticism_score":0, 
            "psychoticism_yes":0,
            "psychoticism_no":0,  
            "sincerity_score":0,
            "sincerity_no":0,
            "sincerity_yes":0,}

    for answer in user_answers:

        if answer.question.scale=='neuroticism':
            if answer.choice =="Այո":
                scores['neuroticism_yes']+=1
            else:
                scores["neuroticism_no"]+=1
            scores['neuroticism_score']+=1
        elif answer.question.scale=='extroversion':
            if answer.choice =="Այո":
                scores['extroversion_yes']+=1
            else:
                scores["extroversion_no"]+=1

            scores['extroversion_score']+=1
        elif answer.question.scale=="psychoticism":
            if answer.choice =="Այո":
                scores['psychoticism_yes']+=1
            else:
                scores["psychoticism_no"]+=1
            scores["psychoticism_score"]+=1
        elif answer.question.scale=="sincerity":
            if answer.choice =="Այո":
                scores['sincerity_yes']+=1
            else:
                scores["sincerity_no"]+=1
        
            scores["sincerity_score"]+=1

    Result.objects.update_or_create(
        user=request.user.username,
        defaults=scores,
    )

    user_prompt=f"""Based on these scores:
    Neuroticism: {scores['neuroticism_yes']} out of {scores['neuroticism_score']}, 
    Extroversion: {scores['extroversion_yes']} out of {scores['extroversion_score']}, 
    Psychoticism: {scores['psychoticism_yes']} out of {scores['psychoticism_score']},  
    Sincerity: {scores['sincerity_yes']} out of {scores['sincerity_score']}.
    
    Provide personalized advice for the user in Armenian."""

    ai_response=get_gemini_response(user_prompt) if user_prompt else ""

    return render(request, 'core/result.html', {'scores': scores, 'response': ai_response} )

    

def ai_chat(request):
    user_prompt = request.GET.get("prompt", "")  
    ai_response = get_gemini_response(user_prompt) if user_prompt else ""
    
    return render(request, "core/chat.html", {"response": ai_response, "prompt": user_prompt})

