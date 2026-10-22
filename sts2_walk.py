import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sts2_helper import req


def walk(node, path=""):
    if isinstance(node, dict):
        for key, value in node.items():
            if "exhaust" in key.lower():
                print(path + "/" + key, "=", json.dumps(value, ensure_ascii=False)[:500])
            walk(value, path + "/" + key)
    elif isinstance(node, list):
        for i, value in enumerate(node):
            walk(value, f"{path}[{i}]")


walk(req("GET", "/state"))
