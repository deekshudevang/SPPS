import pickle
import os
import pandas as pd
import numpy as np

class Predictor:
    def __init__(self):
        # Professional path resolution
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.model_path = os.path.join(base_dir, 'ml', 'model.pkl')
        self.le_path = os.path.join(base_dir, 'ml', 'label_encoder.pkl')
        
        try:
            with open(self.model_path, 'rb') as f:
                self.pipeline = pickle.load(f)
            with open(self.le_path, 'rb') as f:
                self.le = pickle.load(f)
        except Exception as e:
            print(f"Error loading professional models: {e}")
            self.pipeline = None
            self.le = None

    def predict(self, student_data):
        if not self.pipeline:
            return {'risk_level': 'unknown', 'predicted_score': 0}

        # Prepare features for prediction
        features = pd.DataFrame([{
            'attendance': student_data.get('attendance', 0),
            'internal_marks': student_data.get('internal_marks', 0),
            'assignment_scores': student_data.get('assignment_scores', 0),
            'participation_level': student_data.get('participation_level', 0),
            'study_hours': student_data.get('study_hours', 0),
            'previous_semester_result': student_data.get('previous_semester_result', 0)
        }])

        prediction_encoded = self.pipeline.predict(features)[0]
        risk_level = self.le.inverse_transform([prediction_encoded])[0]
        
        # Professional score estimation based on class probabilities
        probs = self.pipeline.predict_proba(features)[0]
        score = round(float(np.max(probs) * 100), 1)
        
        return {
            'risk_level': risk_level,
            'predicted_score': score
        }

    def get_recommendation(self, score):
        """
        Generates AI recommendations based on predicted score.
        Matches portfolio-ready requirements.
        """
        if score < 40:
            return "High Risk: Increase study hours, focus on weak subjects"
        elif 40 <= score <= 70:
            return "Moderate: Practice regularly and revise concepts"
        else:
            return "Good Performance: Keep up the good work"
