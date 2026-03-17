import pickle
import os
import pandas as pd

def predict(data):
    """
    Standard interface for student performance prediction.
    :param data: List or Dict of features
    :return: Predicted risk level (high, average, at_risk)
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, 'model.pkl')
    le_path = os.path.join(base_dir, 'label_encoder.pkl')

    with open(model_path, 'rb') as f:
        pipeline = pickle.load(f)
    with open(le_path, 'rb') as f:
        le = pickle.load(f)

    # Convert incoming data to DataFrame for the pipeline
    if isinstance(data, list):
        features = pd.DataFrame([data], columns=[
            'attendance', 'internal_marks', 'assignment_scores', 
            'participation_level', 'study_hours', 'previous_semester_result'
        ])
    else:
        features = pd.DataFrame([data])
    
    prediction_encoded = pipeline.predict(features)[0]
    result = le.inverse_transform([prediction_encoded])[0]
    
    return result
