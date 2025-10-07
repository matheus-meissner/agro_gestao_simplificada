"""
Leitura/Gravação de arquivos JSON e LOG (texto).
"""
import json, os, datetime
from typing import List, Dict

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
JSON_PATH = os.path.join(DATA_DIR, "colheitas.json")
LOG_PATH = os.path.join(DATA_DIR, "log.txt")

os.makedirs(DATA_DIR, exist_ok=True)

def carregar_json() -> List[Dict]:
    if not os.path.exists(JSON_PATH):
        return []
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_json(colheitas: List[Dict]):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(colheitas, f, ensure_ascii=False, indent=2)

def log(msg: str):
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")
