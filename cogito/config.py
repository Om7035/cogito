import json
import os

CONFIG_PATH = os.path.expanduser("~/.cogito_config.json")

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "cache_dir": "cache",
        "llm_model": "gpt-4",
        "max_workers": 5
    }

def save_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)
