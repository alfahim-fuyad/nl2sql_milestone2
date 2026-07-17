import re
import json
import os
from rapidfuzz import fuzz, process


def _load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        data.pop("_comment", None)
    return data


def _normalize(text):
    text = text.lower().replace("_", " ")
    text = re.sub(r"\([^)]*\)", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def match_column(word, schema, synonyms_path="knowledge/synonyms.json", threshold=70):
    if not word or not schema:
        return None
    synonyms = _load_json(synonyms_path, {})
    word_norm = _normalize(word)
    lookup = {_normalize(col): col for col in schema}
    lookup.update({col.lower(): col for col in schema})
    cols = list(lookup.keys())

    result = process.extractOne(word_norm, cols, scorer=fuzz.token_sort_ratio)
    if result and result[1] >= threshold:
        return lookup[result[0]]

    for key in (word_norm, word.lower().strip()):
        if key in synonyms:
            result = process.extractOne(_normalize(synonyms[key]), cols, scorer=fuzz.token_sort_ratio)
            if result and result[1] >= threshold:
                return lookup[result[0]]
    return None


def find_columns_with_positions(text, schema,
                                 synonyms_path="knowledge/synonyms.json",
                                 stopwords_path="knowledge/stopwords.json",
                                 threshold=72):
    synonyms = _load_json(synonyms_path, {})
    stopwords = set(_load_json(stopwords_path, []) if os.path.exists(stopwords_path) else [])

    raw_tokens = [{"word": m.group(), "position": m.start()}
                  for m in re.finditer(r"[a-z0-9]+", text.lower())]
    if not raw_tokens:
        return []

    core_tokens = [t for t in raw_tokens if t["word"] not in stopwords] or raw_tokens

    col_specs = []
    for col in schema:
        norm = _normalize(col)
        if not norm:
            continue
        words = norm.split()
        core = [w for w in words if w not in stopwords] or words
        col_specs.append({"column": col, "core": core, "phrase": " ".join(core)})

    best = {}
    n_tokens = len(core_tokens)

    for n in range(min(max((len(s["core"]) for s in col_specs), default=1), n_tokens), 0, -1):
        sized = [s for s in col_specs if len(s["core"]) == n]
        for i in range(n_tokens - n + 1):
            window = core_tokens[i:i + n]
            phrase = " ".join(t["word"] for t in window)
            pos = window[0]["position"]
            candidates = {phrase}
            if n == 1 and phrase in synonyms:
                candidates.add(_normalize(synonyms[phrase]))
            for spec in sized:
                score = max(fuzz.token_sort_ratio(c, spec["phrase"]) for c in candidates)
                if score >= threshold:
                    prev = best.get(spec["column"])
                    if prev is None or score > prev["score"]:
                        best[spec["column"]] = {"column": spec["column"],
                                                 "position": pos, "score": score}

    full_phrase = " ".join(t["word"] for t in core_tokens)
    for spec in col_specs:
        if spec["column"] in best:
            continue
        score = fuzz.token_set_ratio(full_phrase, spec["phrase"])
        if score < max(threshold, 80):
            continue
        pos = core_tokens[0]["position"]
        for t in core_tokens:
            if any(fuzz.ratio(t["word"], w) >= 85 for w in spec["core"]):
                pos = t["position"]
                break
        best[spec["column"]] = {"column": spec["column"], "position": pos, "score": score}

    return sorted(best.values(), key=lambda r: (-r["score"], r["position"]))
