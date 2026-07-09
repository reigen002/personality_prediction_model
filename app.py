"""
app.py — Flask backend for personality prediction
"""
from flask import Flask, request, jsonify, render_template
import joblib
import numpy as np
import json
from pathlib import Path

app = Flask(__name__)

TRAITS = ['O', 'C', 'E', 'A', 'N']

# Which of the 25 answers belong to each trait (0-indexed)
TRAIT_QUESTIONS = {
    'O': slice(0,  5),
    'C': slice(5,  10),
    'E': slice(10, 15),
    'A': slice(15, 20),
    'N': slice(20, 25),
}

TRAIT_META = {
    'O': {
        'name': 'Openness',
        'icon': '🎨',
        'high': 'Creative, curious, and imaginative. You love exploring new ideas.',
        'low':  'Practical and grounded. You prefer familiar routines and clear facts.',
        'color': '#a78bfa',
    },
    'C': {
        'name': 'Conscientiousness',
        'icon': '📋',
        'high': 'Organized, disciplined, and goal-driven. You follow through on plans.',
        'low':  'Flexible and spontaneous. You adapt to situations as they arise.',
        'color': '#34d399',
    },
    'E': {
        'name': 'Extraversion',
        'icon': '🌟',
        'high': 'Outgoing, energetic, and sociable. You thrive around people.',
        'low':  'Thoughtful and introspective. You recharge in quiet environments.',
        'color': '#fbbf24',
    },
    'A': {
        'name': 'Agreeableness',
        'icon': '🤝',
        'high': 'Warm, cooperative, and empathetic. You put others first.',
        'low':  'Direct and assertive. You prioritize objectivity over harmony.',
        'color': '#f472b6',
    },
    'N': {
        'name': 'Neuroticism',
        'icon': '🌊',
        'high': 'Emotionally sensitive. You experience feelings deeply and intensely.',
        'low':  'Emotionally stable and resilient. You stay calm under pressure.',
        'color': '#60a5fa',
    },
}

# Load models once at startup
models = {}
for t in TRAITS:
    path = Path(f'models/{t}_model.pkl')
    if path.exists():
        models[t] = joblib.load(path)

summary = {}
summary_path = Path('models/summary.json')
if summary_path.exists():
    with open(summary_path) as f:
        summary = json.load(f)


@app.route('/')
def index():
    return render_template('index.html', summary=summary)


@app.route('/predict', methods=['POST'])
def predict():
    if not models:
        return jsonify({'error': 'Models not loaded. Run train.py first.'}), 500

    data = request.get_json()
    answers = data.get('answers', [])

    if len(answers) != 25:
        return jsonify({'error': f'Expected 25 answers, got {len(answers)}'}), 400

    X = np.array(answers, dtype=float).reshape(1, -1)
    raw  = np.array(answers, dtype=float)  # for direct score computation
    result = {}

    for t in TRAITS:
        model = models[t]
        pred  = int(model.predict(X)[0])

        # Score = mean of the 5 trait-specific answers, normalised to 0–100%
        # This gives smooth, meaningful scores regardless of model confidence
        trait_mean = raw[TRAIT_QUESTIONS[t]].mean()          # 1.0 – 5.0
        score_pct  = round((trait_mean - 1) / 4 * 100, 1)   # 0 – 100 %

        meta = TRAIT_META[t]
        result[t] = {
            'name':        meta['name'],
            'icon':        meta['icon'],
            'label':       'High' if pred == 1 else 'Low',
            'score':       score_pct,
            'description': meta['high'] if pred == 1 else meta['low'],
            'color':       meta['color'],
        }

    return jsonify(result)


@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'models_loaded': list(models.keys()),
        'total': len(models),
    })


if __name__ == '__main__':
    print("\n  Personality Prediction App")
    print(f"  Models loaded: {list(models.keys())}")
    print("  Open http://localhost:5000\n")
    app.run(debug=True, port=5000)
