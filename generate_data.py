"""
generate_data.py
Generates a realistic synthetic Big Five (OCEAN) personality dataset.
25 Likert-scale questions (5 per trait), 2000 samples.
"""
import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)
N = 2000

TRAITS = ['O', 'C', 'E', 'A', 'N']

# Realistic inter-trait correlation matrix (symmetric, Big Five research-based)
# O, C, E, A, N
CORR = np.array([
    [ 1.00,  0.25,  0.28,  0.20, -0.20],
    [ 0.25,  1.00,  0.20,  0.30, -0.45],
    [ 0.28,  0.20,  1.00,  0.35, -0.38],
    [ 0.20,  0.30,  0.35,  1.00, -0.55],
    [-0.20, -0.45, -0.38, -0.55,  1.00],
])
STD = np.array([0.15, 0.15, 0.15, 0.15, 0.15])
COV = np.outer(STD, STD) * CORR   # always symmetric PSD

MEAN = [0.55, 0.55, 0.55, 0.55, 0.45]   # slight positive skew except N

# Sample latent trait scores
latent = np.random.multivariate_normal(MEAN, COV, N)
latent = np.clip(latent, 0.0, 1.0)

data = {}

for i, trait in enumerate(TRAITS):
    for q in range(5):
        col = f'Q{i * 5 + q + 1}'
        # More per-question noise so questions don't perfectly predict the trait mean
        noise = np.random.normal(0, 0.14, N)
        score = latent[:, i] + noise
        # Map (0–1) → Likert (1–5)
        likert = np.clip(np.round(score * 4 + 1), 1, 5).astype(int)
        data[col] = likert

df = pd.DataFrame(data)

# Compute per-trait score (mean of 5 questions, 1–5 scale)
for i, trait in enumerate(TRAITS):
    qs = [f'Q{i * 5 + q + 1}' for q in range(5)]
    df[f'{trait}_score'] = df[qs].mean(axis=1)

    # Probabilistic label using sigmoid boundary + uniform noise
    # This creates genuine uncertainty near the midpoint (score ≈ 3.0)
    # so the model cannot achieve perfect separation
    scores = df[f'{trait}_score'].values
    probs = 1 / (1 + np.exp(-2.5 * (scores - 3.0)))  # sigmoid centred at 3.0
    noise  = np.random.uniform(-0.18, 0.18, N)        # boundary noise ±18%
    probs  = np.clip(probs + noise, 0.05, 0.95)       # never allow pure 0 or 1
    df[f'{trait}_label'] = (np.random.uniform(0, 1, N) < probs).astype(int)

Path('data').mkdir(exist_ok=True)
df.to_csv('data/personality_dataset.csv', index=False)
print(f"✓ Dataset generated: {N} samples → data/personality_dataset.csv")
print(f"  Columns: {list(df.columns)}")
for t in TRAITS:
    pct = df[f'{t}_label'].mean() * 100
    print(f"  {t}: {pct:.1f}% High")
