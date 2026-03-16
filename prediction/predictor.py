import pickle
import os
import pandas as pd
import numpy as np

class Predictor:
    def __init__(self, model_name='randomforest'):
        # Dynamic path resolution to ensure it works in various environments
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.model_path = os.path.join(base_dir, 'ml', 'models', f'{model_name.lower()}_model.pkl')
        self.scaler_path = os.path.join(base_dir, 'ml', 'models', 'scaler.pkl')
        self.le_path = os.path.join(base_dir, 'ml', 'models', 'label_encoder.pkl')
        
        try:
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            with open(self.scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            with open(self.le_path, 'rb') as f:
                self.le = pickle.load(f)
        except Exception as e:
            print(f"Error loading models: {e}")
            self.model = None
            self.scaler = None
            self.le = None

    def predict(self, student_data):
        if not self.model:
            return None, None

        # Prepare features for prediction
        features = pd.DataFrame([{
            'attendance': student_data.attendance,
            'internal_marks': student_data.internal_marks,
            'assignment_scores': student_data.assignment_scores,
            'participation_level': student_data.participation_level,
            'study_hours': student_data.study_hours,
            'previous_semester_result': student_data.previous_semester_result
        }])

        scaled_features = self.scaler.transform(features)
        prediction_encoded = self.model.predict(scaled_features)[0]
        risk_level = self.le.inverse_transform([prediction_encoded])[0]
        
        # Simple score estimation (academic demo purpose)
        probs = self.model.predict_proba(scaled_features)[0]
        score = round(float(np.max(probs) * 100), 2)
        
        return risk_level, score

    def get_recommendation(self, student_data, risk_level):
        if risk_level == 'at_risk':
            if student_data.attendance < 75:
                return "Urgent: Low attendance detected. Please attend more classes to improve your grades."
            if student_data.study_hours < 4:
                return "Low study hours. Setting aside a dedicated time for self-study is recommended."
            return "Performance is declining. Consider attending peer tutoring sessions."
        elif risk_level == 'average':
            return "Steady progress. Focus on increasing participation to boost your internal marks."
        else:
            return "Excellent work! Keep maintaining your current study habits and participation."
