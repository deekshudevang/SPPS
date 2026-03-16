import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, precision_recall_fscore_support
import pickle
import json
import os

# Create synthetic data
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

# Main pipeline
def train_pipeline():
    print("Generating data...")
    df = generate_data()
    os.makedirs('ml/datasets', exist_ok=True)
    df.to_csv('ml/datasets/student_data.csv', index=False)
    
    X = df.drop('performance', axis=1)
    y = df['performance']
    
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    models = {
        'LogisticRegression': LogisticRegression(max_iter=1000),
        'DecisionTree': DecisionTreeClassifier(),
        'RandomForest': RandomForestClassifier(n_estimators=100)
    }
    
    os.makedirs('ml/models', exist_ok=True)
    report_data = {}

    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
        
        acc = accuracy_score(y_test, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted')
        
        report_data[name] = {
            'accuracy': round(acc, 4),
            'precision': round(precision, 4),
            'recall': round(recall, 4),
            'f1_score': round(f1, 4)
        }
        
        print(f"{name} Accuracy: {acc:.4f}")
        
        with open(f'ml/models/{name.lower()}_model.pkl', 'wb') as f:
            pickle.dump(model, f)
    
    with open('ml/models/scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    with open('ml/models/label_encoder.pkl', 'wb') as f:
        pickle.dump(le, f)
        
    with open('ml/models/metrics.json', 'w') as f:
        json.dump(report_data, f, indent=4)
        
    print("Pipeline completed. Models and metrics saved.")

if __name__ == "__main__":
    train_pipeline()

if __name__ == "__main__":
    train_pipeline()
