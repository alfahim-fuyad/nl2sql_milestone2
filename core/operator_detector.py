import re
import json


def load_operators(path="knowledge/operators.json"):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data.pop("_comment", None)
    return data


def detect_operators(text, operators_path="knowledge/operators.json"):
    operators = load_operators(operators_path)
    text_lower = text.lower()
    phrases = sorted(operators.keys(), key=len, reverse=True)
    found = []
    used = set()

    for phrase in phrases:
        for m in re.finditer(re.escape(phrase), text_lower):
            start, end = m.start(), m.end()
            positions = set(range(start, end))
            if positions & used:
                continue
            before = text_lower[start - 1] if start > 0 else " "
            after = text_lower[end] if end < len(text_lower) else " "
            if before not in (" ", "\t") and start != 0:
                continue
            if after not in (" ", "\t") and end != len(text_lower):
                continue
            found.append({"symbol": operators[phrase], "position": start})
            used.update(positions)

    found.sort(key=lambda x: x["position"])
    return found
