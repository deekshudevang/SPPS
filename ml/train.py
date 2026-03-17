from sklearn.pipeline import Pipeline
import pickle
import json
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier

# Create synthetic data for demo purposes
def generate_data(n_samples=1000):
    np.random.seed(42)
    data = {
        'attendance': np.random.uniform(60, 100, n_samples),
        'internal_marks': np.random.uniform(10, 50, n_samples),
        'assignment_scores': np.random.uniform(10, 50, n_samples),
        'participation_level': np.random.randint(1, 11, n_samples),
        'study_hours': np.random.uniform(1, 10, n_samples),
        'previous_semester_result': np.random.uniform(40, 100, n_samples)
    }
    df = pd.DataFrame(data)
    
    # Heuristic scoring logic for labels
    score = (
        0.3 * df['attendance'] + 
        0.2 * df['internal_marks'] * 2 + 
        0.15 * df['assignment_scores'] * 2 + 
        0.1 * df['participation_level'] * 10 + 
        0.15 * df['study_hours'] * 10 + 
        0.1 * df['previous_semester_result']
    )
    score += np.random.normal(0, 5, n_samples)
    
    def classify(s):
        if s > 80: return 'high'
        if s > 60: return 'average'
        return 'at_risk'
    
    df['performance'] = pd.Series(score).apply(classify)
    return df

def train_pipeline():
    """
    Trains the model using a scikit-learn Pipeline and saves to a unified pkl file.
    """
    print("Initializing professional training pipeline...")
    df = generate_data()
    
    # Ensure ml directory exists
    os.makedirs('ml', exist_ok=True)
    df.to_csv('ml/dataset.csv', index=False)
    
    X = df.drop('performance', axis=1)
    y = df['performance']
    
    # We serialize the LabelEncoder separately as it's for the target, 
    # but the features go through the Pipeline.
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
    
    # Define a professional Pipeline
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    
    print("Fitting Random Forest Pipeline...")
    pipeline.fit(X_train, y_train)
    
    # Calculate performance metrics for the portfolio dashboard
    y_pred = pipeline.predict(X_test)
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support
    acc = accuracy_score(y_test, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted')
    
    metrics_report = {
        'RandomForest': {
            'accuracy': round(acc, 4),
            'precision': round(precision, 4),
            'recall': round(recall, 4),
            'f1_score': round(f1, 4)
        }
    }
    
    # Save unified model and auxiliary files
    with open('ml/model.pkl', 'wb') as f:
        pickle.dump(pipeline, f)
    
    with open('ml/label_encoder.pkl', 'wb') as f:
        pickle.dump(le, f)
        
    with open('ml/metrics.json', 'w') as f:
        json.dump(metrics_report, f, indent=4)
        
    print("Model and metrics successfully saved to ml/")

if __name__ == "__main__":
    train_pipeline()
