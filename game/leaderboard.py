import json
from pathlib import Path

LEADERBOARD_FILE = Path("leaderboard.json")

def load_leaderboard():
    if LEADERBOARD_FILE.exists():
        with open(LEADERBOARD_FILE, 'r') as f:
            return json.load(f)
    return []

def save_leaderboard(scores):
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(scores, f, indent=2)

def add_score(name, score):
    scores = load_leaderboard()
    scores.append({"name": name, "score": score})
    scores = sorted(scores, key=lambda x: x["score"], reverse=True)[:10]
    save_leaderboard(scores)
