import json
import os


def load_json(path):

    if not os.path.exists(path):
        raise FileNotFoundError(path)

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_folder(folder):

    if not os.path.exists(folder):
        os.makedirs(folder)
