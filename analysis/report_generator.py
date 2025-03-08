import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from core.models import Result

class ResultAnalyzer:
    def __init__(self, test_id):
        self.test_id = test_id
        self.df = self._load_data()
    
    def _load_data(self):
        results = Result.objects.filter(session__test_id=self.test_id)
        data = []
        for result in results:
            row = result.results['traits'].copy()
            row['user'] = result.session.candidate.username
            data.append(row)
        return pd.DataFrame(data)
    
    def generate_summary_report(self):
        plt.figure(figsize=(10, 6))
        self.df.mean().plot(kind='bar')
        plt.title('Average Trait Scores')
        plt.ylabel('Score')
        plt.xticks(rotation=45)
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        
        return {
            'summary_stats': self.df.describe().to_dict(),
            'chart': image_base64
        }