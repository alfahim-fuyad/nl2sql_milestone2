import re


def extract_numbers(text):
    return [{"value": m.group(), "position": m.start()}
            for m in re.finditer(r"\b\d+(?:\.\d+)?\b", text)]


def match_categorical_values(text, schema):
    text_lower = text.lower()
    matches = []
    matched_cols = set()

    for col, info in schema.items():
        if "int" in info["dtype"] or "float" in info["dtype"]:
            continue
        for sample in info["sample_values"]:
            pattern = r"(?<![a-z0-9])" + re.escape(str(sample).lower()) + r"(?![a-z0-9])"
            if re.search(pattern, text_lower) and col not in matched_cols:
                matches.append({"column": col, "value": str(sample)})
                matched_cols.add(col)
                break

    return matches
