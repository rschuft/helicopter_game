import json
from pathlib import Path

CONFIG_DIR = Path(__file__).parent.parent / "config"
CONFIG_DIR.mkdir(exist_ok=True)
SETTINGS_FILE = CONFIG_DIR / "settings.json"

# Default settings
DEFAULT_SETTINGS = {
    "WIDTH": 800,
    "HEIGHT": 600,
    "FPS": 60,
    "FULLSCREEN": True
}

def load_settings():
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    else:
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)

settings = load_settings()
WIDTH = settings.get("WIDTH", DEFAULT_SETTINGS["WIDTH"])
HEIGHT = settings.get("HEIGHT", DEFAULT_SETTINGS["HEIGHT"])
FPS = settings.get("FPS", DEFAULT_SETTINGS["FPS"])
FULLSCREEN = settings.get("FULLSCREEN", DEFAULT_SETTINGS["FULLSCREEN"])