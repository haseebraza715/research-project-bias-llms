import json
from pathlib import Path

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


def load_json(name: str):
    path = CONFIG_DIR / name
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_profiles():
    return load_json("profiles.json")


def load_prompts():
    return load_json("prompts.json")


def load_settings():
    return load_json("settings.json")

