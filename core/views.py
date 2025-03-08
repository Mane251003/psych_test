from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from .models import Question, Answer, Result, PsychoTest, TestSession, Response
from django.utils.timezone import now

from django.http import JsonResponse
from django.db.models import Max
from .forms import AnswerForm

from .utils.gemini import get_gemini_response
import openai
from openai import OpenAI


from core.scoring import TestEvaluator

def test_list(request):
    tests=PsychoTest.objects.filter(is_active=True)
    return render(request, 'core/test_list.html', {'tests':tests})

def start_test(request,test_id):
    test=get_object_or_404(PsychoTest, id=test_id)
    questions=test.questions.all().order_by('order')

  
    session, created =TestSession.objects.get_or_create(
        candidate=request.user, 
        test=test,
        is_completed=False)

    if request.method=='POST':
        for question in questions:
            field_name=f'question_{question.id}'
            user_input=request.POST.get(field_name, '').strip()

            if question.question_type=='rating_scale':
                scale_val=int(user_input) if user_input else None
                Response.objects.update_or_create(
                    session=session,
                    question=question,
                    response_time=now(),
                    defaults={'scale_value': scale_val}
                )
            elif question.question_type=='multiple_choice':
                Response.objects.update_or_create(
                    session=session,
                    question=question,
                    response_time=now(),
                    defaults={'choice': user_input}
                )
            elif question.question_type=='open_text':
                Response.objects.update_or_create(
                    session=session,
                    question=question,
                    defaults={'choice': user_input}
                )

        session.is_completed=True
        session.end_time=now()
        session.save()


        evaluator=TestEvaluator(session)
        results=evaluator.calculate_results()

        Result.objects.update_or_create(
            session=session,
            defaults={
                 'theoretical_scores': results['theoretical_scores'], 
                 'scenario_analysis': results['scenario_analysis'],
                 'scale_evaluations': results['scale_evaluations'],
                 'free_response_analysis': results.get('free_response_analysis', '') 

            }
        )

        return redirect('result', session_id=session.id)
    


    context={'test':test,
             'session':session,
             'questions':questions}
    
    return render(request, 'core/test.html', context)

def submit_response(request):
    if request.method=='POST':
        session_id=request.POST.get('session_id')
        question_id=request.POST.get('question_id')
        answer_id=request.POST.get('answer_id')

        session=get_object_or_404(TestSession, id=session_id, candidate=request.user)
        question=get_object_or_404(Question, id=question_id, test=session.test)
        answer=get_object_or_404(Answer, id=answer_id, question=question)
        Response.objects.create(
            session=session,
            question=question,
            answer=answer
        )
        return JsonResponse({'status': "success"})
    return JsonResponse({'status': 'error'}, status=400)

def result(request, session_id):
    session=get_object_or_404(TestSession, id=session_id, candidate=request.user)
    try:
        result=Result.objects.get(session=session)
    except Result.DoesNotExist:
        return render(request, 'core/no_result.html', {'session':session})
  
    return render(request, 'core/result.html', {'result': result, 'session':session})
   
   
   
  #  result=get_object_or_404(Result, session=session)
 


#avel
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
    return render(request, 'core/testt.html', {'questions': questions})

def resultt(request):
    scores=Answer.objects.filter(user=request.user.username).first()
    print(scores)
    if not scores:
        return render(request, 'core/result.html', {'error':'you did not pass the test'})
    return render(request, 'core/result.html', {'scores':scores})


def resulttt(request):
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

