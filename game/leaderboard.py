import json
from pathlib import Path

CONFIG_DIR = Path(__file__).parent.parent / "config"
CONFIG_DIR.mkdir(exist_ok=True)
LEADERBOARD_FILE = CONFIG_DIR / "leaderboard.json"

# Always keep only top N scores
def load_leaderboard(max_entries=10):
    if LEADERBOARD_FILE.exists():
        try:
            with open(LEADERBOARD_FILE, 'r') as f:
                scores = json.load(f)
                # Validate structure
                if not isinstance(scores, list):
                    return []
                for entry in scores:
                    if not isinstance(entry, dict) or 'name' not in entry or 'score' not in entry:
                        return []
                # Sort and trim
                scores = sorted(scores, key=lambda x: x.get("score", 0), reverse=True)[:max_entries]
                return scores
        except Exception:
            return []
    return []

def save_leaderboard(scores, max_entries=10):
    # Always keep only top N
    scores = sorted(scores, key=lambda x: x.get("score", 0), reverse=True)[:max_entries]
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(scores, f, indent=2)

def add_score(name, score, max_entries=10):
    # Clean name input
    if not name or not isinstance(name, str) or not name.strip():
        name = "Anonymous"
    name = name.strip()[:16]
    try:
        score = int(score)
    except Exception:
        score = 0
    scores = load_leaderboard(max_entries)
    scores.append({"name": name, "score": score})
    save_leaderboard(scores, max_entries)
