import json
from pathlib import Path

CONFIG_DIR = Path(__file__).parent.parent / "config"
CONFIG_DIR.mkdir(exist_ok=True)
LEADERBOARD_FILE = CONFIG_DIR / "leaderboard.json"

def load_leaderboard():
    if LEADERBOARD_FILE.exists():
        with open(LEADERBOARD_FILE, 'r') as f:
            return json.load(f)
    return []

def save_leaderboard(scores):
    # Always keep only top 10
    scores = sorted(scores, key=lambda x: x["score"], reverse=True)[:10]
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(scores, f, indent=2)

def add_score(name, score):
    scores = load_leaderboard()
    scores.append({"name": name, "score": score})
    scores = sorted(scores, key=lambda x: x["score"], reverse=True)[:10]
    save_leaderboard(scores)
