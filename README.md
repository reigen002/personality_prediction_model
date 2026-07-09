# 🧠 Personality Predictor — Big Five (OCEAN)

A machine learning system that predicts your **Big Five personality traits** from a 25-question questionnaire, served via an interactive web app.

---

## 📌 What It Does

Takes 25 Likert-scale (1–5) questionnaire responses and predicts whether you score **High or Low** on each of the five core personality dimensions:

| Trait | Description |
|---|---|
| 🎨 **Openness** | Creativity, curiosity, imagination |
| 📋 **Conscientiousness** | Organization, discipline, goal-driven |
| 🌟 **Extraversion** | Sociability, energy, assertiveness |
| 🤝 **Agreeableness** | Empathy, cooperation, warmth |
| 🌊 **Neuroticism** | Emotional sensitivity, stress-proneness |

Results are shown as an **animated OCEAN radar chart** with per-trait score bars.

---

## 🗂️ Project Structure

```
personality_prediction_model/
├── data/
│   └── personality_dataset.csv    # Generated synthetic dataset (2000 samples)
├── models/
│   ├── O_model.pkl                # Saved model — Openness
│   ├── C_model.pkl                # Saved model — Conscientiousness
│   ├── E_model.pkl                # Saved model — Extraversion
│   ├── A_model.pkl                # Saved model — Agreeableness
│   ├── N_model.pkl                # Saved model — Neuroticism
│   └── summary.json               # Training results (best model, F1, accuracy)
├── templates/
│   └── index.html                 # Quiz UI (4 screens: welcome → quiz → loading → results)
├── static/
│   ├── style.css                  # Dark glassmorphism CSS
│   └── app.js                     # Quiz logic, Chart.js radar, fetch/predict
├── generate_data.py               # Synthetic OCEAN dataset generator
├── train.py                       # Model training & evaluation script
├── app.py                         # Flask REST API
└── requirements.txt               # Python dependencies
```

---

## ⚙️ Setup & Usage

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate synthetic dataset

```bash
python generate_data.py
```

Outputs `data/personality_dataset.csv` — 2000 samples, 25 questionnaire columns (Q1–Q25) plus OCEAN score/label columns.

### 3. Train models

```bash
python train.py
```

Trains **3 classifiers per trait** (Logistic Regression, Random Forest, Gradient Boosting), selects the best via 5-fold cross-validation F1, and saves the winner to `models/`.

A summary of model performance is printed and saved to `models/summary.json`.

### 4. Run the web app

```bash
python app.py
```

Open **http://localhost:5000** in your browser.

---

## 🤖 ML Details

### Dataset
- **2,000 synthetic samples** generated with realistic Big Five inter-trait correlations (research-based correlation matrix)
- **25 Likert-scale questions** (Q1–Q25), 5 per trait in O → C → E → A → N order
- **Labels**: trait mean ≥ 3.0 → High (1), < 3.0 → Low (0)

### Models Trained (per trait)

| Model | Notes |
|---|---|
| Logistic Regression | Baseline; linear; fast |
| Random Forest | Ensemble; non-linear |
| Gradient Boosting | Boosted trees; typically strongest |

Best model selected per trait by **5-fold CV F1 score** on training set, then evaluated on held-out 20% test split.

### Training Results (on synthetic data)

| Trait | Best Model | Test Accuracy | Test F1 |
|---|---|---|---|
| Openness | Logistic Regression | 1.000 | 1.000 |
| Conscientiousness | Logistic Regression | 1.000 | 1.000 |
| Extraversion | Logistic Regression | 1.000 | 1.000 |
| Agreeableness | Logistic Regression | 1.000 | 1.000 |
| Neuroticism | Logistic Regression | 1.000 | 1.000 |

> **Note:** Perfect scores are expected on synthetic data — the same statistical process generates both the features and labels, so the signal is clean. On real-world questionnaire data, expect F1 in the 0.70–0.85 range.

### API Endpoint

**`POST /predict`**

Request:
```json
{ "answers": [3, 4, 2, 5, 1, ...] }  // 25 integers, values 1–5
```

Response:
```json
{
  "O": { "name": "Openness", "label": "High", "score": 78.3, "description": "...", "icon": "🎨", "color": "#a78bfa" },
  "C": { ... },
  ...
}
```

---

## 🌐 Web App Screens

| Screen | Description |
|---|---|
| **Welcome** | Intro card with trait pills and model summary |
| **Quiz** | 5 pages × 5 questions; Likert 1–5 buttons; progress bar & dot navigation |
| **Loading** | Animated spinner with per-trait completion indicators |
| **Results** | OCEAN radar chart (Chart.js) + 5 trait cards with score bars and descriptions |

---

## 📦 Dependencies

```
scikit-learn >= 1.4
pandas       >= 2.0
numpy        >= 1.26
flask        >= 3.0
joblib       >= 1.3
```

---

## 🔄 Re-training with Real Data

To use a real questionnaire dataset (e.g., from [Open Psychometrics IPIP](https://openpsychometrics.org/_rawdata/)):

1. Place your CSV in `data/personality_dataset.csv`
2. Ensure columns `Q1`–`Q25` contain Likert scores (1–5) and `O_label`, `C_label`, `E_label`, `A_label`, `N_label` contain binary labels (0/1)
3. Re-run `python train.py`
