"""
train.py
Trains 3 classifiers per OCEAN trait, picks the best by F1, saves models.
"""
import pandas as pd
import numpy as np
import joblib
import json
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import classification_report

TRAITS = ['O', 'C', 'E', 'A', 'N']
TRAIT_NAMES = {
    'O': 'Openness',
    'C': 'Conscientiousness',
    'E': 'Extraversion',
    'A': 'Agreeableness',
    'N': 'Neuroticism',
}

def build_models():
    return {
        'Logistic Regression': Pipeline([
            ('scaler', StandardScaler()),
            ('clf', LogisticRegression(max_iter=1000, C=1.0, random_state=42))
        ]),
        'Random Forest': RandomForestClassifier(
            n_estimators=150, max_depth=8, random_state=42, n_jobs=-1
        ),
        'Gradient Boosting': GradientBoostingClassifier(
            n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42
        ),
    }

def train():
    print("=" * 50)
    print("  Personality Prediction — Model Training")
    print("=" * 50)

    df = pd.read_csv('data/personality_dataset.csv')
    feature_cols = [f'Q{i+1}' for i in range(25)]
    X = df[feature_cols].values

    Path('models').mkdir(exist_ok=True)
    summary = {}

    for trait in TRAITS:
        print(f"\n[{TRAIT_NAMES[trait]}]")
        y = df[f'{trait}_label'].values

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        best_model = None
        best_score = 0.0
        best_name = ''
        model_scores = {}

        for name, model in build_models().items():
            cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='f1', n_jobs=-1)
            mean_f1 = cv_scores.mean()
            model_scores[name] = round(mean_f1, 4)
            print(f"  {name:<25} CV F1 = {mean_f1:.3f} ± {cv_scores.std():.3f}")
            if mean_f1 > best_score:
                best_score = mean_f1
                best_model = model
                best_name = name

        # Final fit on full training set
        best_model.fit(X_train, y_train)
        y_pred = best_model.predict(X_test)
        report = classification_report(y_test, y_pred, output_dict=True)
        test_f1 = report['weighted avg']['f1-score']
        test_acc = report['accuracy']

        joblib.dump(best_model, f'models/{trait}_model.pkl')
        print(f"  ✓ Best: {best_name} | Test Acc={test_acc:.3f} | Test F1={test_f1:.3f}")
        print(f"  → Saved: models/{trait}_model.pkl")

        summary[trait] = {
            'name': TRAIT_NAMES[trait],
            'best_model': best_name,
            'cv_f1': round(best_score, 4),
            'test_accuracy': round(test_acc, 4),
            'test_f1': round(test_f1, 4),
            'all_model_scores': model_scores,
        }

    with open('models/summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 50)
    print("  Training Complete!")
    print("=" * 50)
    print("\nModel Performance Summary:")
    print(f"  {'Trait':<20} {'Best Model':<26} {'Acc':>6} {'F1':>6}")
    print("  " + "-" * 62)
    for t, v in summary.items():
        print(f"  {v['name']:<20} {v['best_model']:<26} {v['test_accuracy']:>6.3f} {v['test_f1']:>6.3f}")
    print()

if __name__ == '__main__':
    train()
