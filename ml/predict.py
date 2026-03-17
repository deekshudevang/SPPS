import pickle
import os
import pandas as pd

def predict(data):
    """
    Standard interface for student performance prediction.
    :param data: List of features [attendance, internal_marks, assignment_scores, participation, study_hours, previous_result]
    :return: Predicted risk level (high, average, at_risk)
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, 'models', 'randomforest_model.pkl')
    scaler_path = os.path.join(base_dir, 'models', 'scaler.pkl')
    le_path = os.path.join(base_dir, 'models', 'label_encoder.pkl')

    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    with open(scaler_path, 'rb') as f:
        scaler = pickle.load(f)
    with open(le_path, 'rb') as f:
        le = pickle.load(f)

    # Convert incoming data to DataFrame for scaler
    features = pd.DataFrame([data], columns=[
        'attendance', 'internal_marks', 'assignment_scores', 
        'participation_level', 'study_hours', 'previous_semester_result'
    ])
    
    scaled_features = scaler.transform(features)
    prediction_encoded = model.predict(scaled_features)[0]
    result = le.inverse_transform([prediction_encoded])[0]
    
    return result
