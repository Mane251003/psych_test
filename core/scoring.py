from collections import defaultdict
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from collections import defaultdict
from .models import TestSession, Response, Trait, Question, Answer, Result



class BigFiveScorerrrr:

    def calculate_results(session_id):
        try:
            session = TestSession.objects.get(id=session_id)
            questions = session.test.questions.all()
            answers = Answer.objects.filter(question__in=questions, user=session.candidate)

            raw_scores = {}
            for question in questions:
                answer = answers.filter(question=question).first()
                if not answer:
                  continue

                trait_code = question.trait.code
                score = answer.value * question.weight

                if trait_code not in raw_scores:
                   raw_scores[trait_code] = 0
                raw_scores[trait_code] += score

       
            max_score = max(raw_scores.values(), default=1)
            normalized_scores = {k: (v / max_score) * 100 for k, v in raw_scores.items()}

     
            result, created = Result.objects.update_or_create(
               session=session,
               defaults={
                'raw_scores': raw_scores,
                'normalized_scores': normalized_scores,
                'interpretation': {}, 
                'recommendations': {}, 
            }
        )
            return result

        except TestSession.DoesNotExist:
            raise ValueError("Invalid session ID")

class BigFiveScorer:
    def __init__(self, session: TestSession):
        self.session=session
        print(f"session is {self.session}")

        # responses is a relative name in Response model 
        self.responses=session.responses.select_related('question__trait')
        print(f'responsesss is {self.responses}')
        self.trait_data=self._load_trait_definitions() #Extraversia, Neuroticism,Agreeableness,Conscientiousness,Openness

    


    #All codes,  Extraversia, Neuroticism,Agreeableness,Conscientiousness,Openness
    def _load_trait_definitions(self):
        traits=Trait.objects.all()
        return {t.code: t for t in traits}
    
    def _validate_session(self):
        if self.session.test.test_type!='BIG5':
            raise ValueError(_('This scorer works only with Big 5 test'))
        
        required_questions=self.session.test.questions.count()
        answered=self.responses.count()
        if answered!=required_questions:
            raise ValueError(_('Missing answers: %(answered)d/%(required)d') % {
                    'answered': answered,
                    'required': required_questions
                })
        
  #  @transaction.atomic
    def calculate_results(self):
        self._validate_session()

        trait_scores, max_scores=self._calculate_base_scores()
        normalized=self._normalize_scores(trait_scores, max_scores)




    
        return {
            'raw_scores': trait_scores,
            'max_scores': max_scores,
            'normalized_scores': normalized,

            'interpretation': self._generate_interpretation(normalized),
            'recommendations': {'ankap':56}
         #   'recommendations': self._generate_recommendations(normalized),
          #  'theoretical_scores': self._calculate_theoretical(),
           # 'scale_evaluations': self._calculate_scale_evaluations()
            
        }
    
    def _calculate_base_scores(self):
        trait_scores=defaultdict(float)
        max_scores=defaultdict(float)
        print('daa')

        for response in self.responses:
            question=response.question
            print(f"question is {question}")
            trait_code=question.trait.code  #extr, op, ..
            print(f"trait code is {trait_code}")
            print(f"base value is {response.scale_value}")

            raw_value=self._calculate_raw_value(response, question)
            print(f'raw value is {raw_value}')
            weighted_value=raw_value*question.weight
            trait_scores[trait_code] += weighted_value
            print(f"trait_scores[trait_code] == {trait_scores[trait_code]}")
            max_scores[trait_code]+=self._get_max_score(question)*question.weight
            print(f"max score is {max_scores}")
        
        return dict(trait_scores), dict(max_scores)


    
    def _calculate_raw_value(self, response, question):
        base_value = response.scale_value
        
        # Հակադարձ միավորում բացասական հարցերի համար
        if question.key == '-':
            if question.question_type == 'rating_scale':
                return (question.scale_max - base_value) + question.scale_min
            
            elif question.question_type in ['yes_no', 'multiple_choice']:
                max_val=self._get_max_score(question)
                return max_val-base_value
            
        return base_value

    def _get_max_score(self, question):
        if question.question_type == 'rating_scale':
            return question.scale_max
        elif question.question_type == 'yes_no':
            return 1
        elif question.question_type == 'multiple_choice':
            return max(choice['value'] for choice in question.multiple_choices)
        return 0
    
    def _normalize_scores(self, trait_scores, max_scores):
        return {
            code: (score/max_scores[code])*100
            for code, score in trait_scores.items()
            if max_scores.get(code, 0)>0
        }
    
    def _generate_interpretation(self, scores):
        return {
            code: self._trait_interpretation(code, score)
            for code, score in scores.items()
        }

    def _trait_interpretation(self, code, score):
        trait=self.trait_data[code]
    
        return {
                'name': trait.name,
                'score': round(score, 1),
                'description': self._get_description(trait, score),
                'graphic': self._generate_score_graphic(score)
            }
    
    def _get_description(self, trait, score):
        if score>=70:
            print(f"high range is {trait.high_range}")
            return trait.high_range
            
        if score<=30:
            return trait.low_range
        return trait.mid_range
      

    def _generate_score_graphic(self, score):
        bars = int(score / 5)
        return '▓' * bars + '░' * (20 - bars)

    def _generate_recommendations(self, scores):
        recommendations = []
        for code, score in scores.items():
            trait = self.trait_data[code]
            
            if score >= 70:
                recs = trait.high_considerations.split(', ')
            elif score <= 30:
                recs = trait.low_considerations.split(', ')
            else:
                continue
            recommendations.extend(recs)
            
        return list(set(recommendations))

    def _calculate_theoretical(self):
        scores = defaultdict(float)
        for response in self.responses.filter(question__question_type='multiple_choice'):
            try:
                selected = next(
                    c for c in response.question.multiple_choices
                    if c['value'] == int(response.choice)
                )
                scores[response.question.trait.code] += selected['value'] * response.question.weight
            except (StopIteration, ValueError, TypeError):
                continue
        return dict(scores)


    def _calculate_scale_evaluations(self):
        scale_data = defaultdict(list)
        for response in self.responses.filter(question__question_type='rating_scale'):
            scale_data[response.question.trait.code].append(response.scale_value) 
        
        return {
            code: sum(values)/len(values) if len(values)>0 else 0
            for code, values in scale_data.items()
        }


      
class TestEvaluator:
    def __init__(self, session):
        self.session = session
        self.responses = session.responses.select_related('question')
        
    def calculate_results(self):
        scores = {
            'theoretical_scores': self._calculate_theoretical(),
            'scale_evaluations': self._calculate_scales(),
            'scenario_analysis': self._analyze_scenarios()
        }
        for response in self.responses.filter(question__question_type='multiple_choice'):
            try:
                # Փնտրել ընտրված արժեքը
                selected = next(
                    (item for item in response.question.multiple_choices 
                     if str(item['value']) == response.choice),
                    None
                )
                if selected:
                    scores[response.question.trait.code] += selected['value'] * response.question.weight
            except:
                pass
        
        if self.session.free_response:
            scores['free_response_analysis'] = self._analyze_free_text()
        
        return scores

    def _calculate_theoretical(self):
        scores = defaultdict(float)
        for response in self.responses.filter(question__question_type='multiple_choice'):
            try:
                option_index=response.question.multiple_choices.index(response.choice)
                scores[response.question.trait.code]+=(option_index+1)*response.question.weight
            except ValueError:
                pass
           
        return scores

    def _calculate_scales(self):
        scale_data = defaultdict(list)
        for response in self.responses.filter(question__question_type='rating_scale'):
            scale_data[response.question.trait].append({
                'score': response.scale_value,
                'max': response.question.scale_max,
                'min': response.question.scale_min
            })
        return self._normalize_scales(scale_data)

    def _analyze_scenarios(self):
        # Implement scenario analysis logic
        return {}

    def _analyze_free_text(self):
        # Implement text analysis logic
        return {"word_count": len(self.session.free_response.split())}

    def _normalize_scales(self, scale_data):
        return {
            trait: sum(item['score'] for item in items)/len(items)
            for trait, items in scale_data.items()
        }