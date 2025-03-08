from collections import defaultdict
from .models import Response

class BigFiveScorer:
    def __init__(self, session):
        self.session=session
        self.scores=defaultdict(float)
        self.weights=defaultdict(float)

    def calculate_scores(self):

        responses=Response.objects.filter(session=self.session)
        for response in responses:
            trait=response.question.trait
            weight=response.question.weight
            value=response.answer.value

            self.scores[trait]+=value*weight
            self.weights[trait]+=weight

        normalized={}
        for trait in self.scores:
            if self.weights[trait]>0:
                normalized[trait]=self.scores[trait]/self.weights[trait]

            else:
                normalized[trait]=0
        return self._interpret_scores(normalized)

    def _interpret_scores(self, scores):
        interpretations={
            'opennes': self._interpret_openness,
            'conscientiousness': self._interpret_conscientiousness,
            'extraversion': self._interpret_extraversion,
            'agreeableness': self._interpret_agreeableness,
            'neuroticism': self._interpret_neuroticism,
        }
        results={'traits':scores, 'interpretations':{}}

        for trait, interpreter in interpretations.items():
            results['interpretations'][trait]=interpreter(scores.get(trait,0))

        return results

        


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
        
        if self.session.free_response:
            scores['free_response_analysis'] = self._analyze_free_text()
            
        return scores

    def _calculate_theoretical(self):
        scores = defaultdict(float)
        for response in self.responses.filter(question__question_type='multiple_choice'):
            try:
                option_index=response.question.multiple_choices.index(response.choice)
                scores[response.question.trait]+=(option_index+1)*response.question.weight
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