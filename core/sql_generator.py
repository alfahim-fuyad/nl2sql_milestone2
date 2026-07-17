import re
from operator_detector import detect_operators
from attribute_matcher import find_columns_with_positions
from value_matcher import extract_numbers, match_categorical_values
from schema_reader import get_numeric_columns

AGG = {"AVG", "MAX", "MIN", "SUM"}
SIMPLE = {">", "<", ">=", "<=", "=", "!=", "<>"}
BETWEEN = {"BETWEEN", "NOT BETWEEN"}
NULL = {"IS NULL", "IS NOT NULL"}

TOP = re.compile(r"\btop\s+(\d+)\b", re.I)
BOT = re.compile(r"\b(?:bottom|lowest|least|worst|minimum)\s+(\d+)\b", re.I)


def _q(name):
    return '"' + name.replace('"', '""') + '"'


def _nearest(pos, matches, allowed=None, exclude=None):
    cands = [c for c in matches
             if (allowed is None or c["column"] in allowed)
             and (exclude is None or c["column"] not in exclude)]
    if not cands:
        return None
    return min(cands, key=lambda c: (abs(c["position"] - pos), -c["score"]))["column"]


def build_query(question, schema, intent,
                operators_path="knowledge/operators.json",
                synonyms_path="knowledge/synonyms.json"):
    filters = []
    used = set()
    numeric = set(get_numeric_columns(schema))
    col_matches = find_columns_with_positions(question, schema, synonyms_path)

    for m in match_categorical_values(question, schema):
        if m["column"] not in used:
            filters.append({"column": m["column"], "operator": "=", "value": m["value"]})
            used.add(m["column"])

    operators = detect_operators(question, operators_path)
    numbers = extract_numbers(question)
    used_nums = set()

    for op in operators:
        sym, pos = op["symbol"], op["position"]
        if sym in {"IN", "NOT IN"}:
            continue

        if sym in NULL:
            col = _nearest(pos, col_matches, exclude=used)
            if col and col not in used:
                filters.append({"column": col, "operator": sym})
                used.add(col)

        elif sym in BETWEEN:
            nums = sorted([n for n in numbers if n["position"] > pos and id(n) not in used_nums],
                          key=lambda n: n["position"])
            if len(nums) >= 2:
                col = _nearest(pos, col_matches, allowed=numeric, exclude=used)
                if col and col not in used:
                    filters.append({"column": col, "operator": sym,
                                    "value": nums[0]["value"], "value2": nums[1]["value"]})
                    used.add(col)
                    used_nums.update([id(nums[0]), id(nums[1])])

        elif sym == "LIKE":
            words = [m for m in re.finditer(r"\S+", question.lower()) if m.start() > pos]
            if words:
                col = _nearest(pos, col_matches, exclude=used)
                if col and col not in used:
                    filters.append({"column": col, "operator": "LIKE",
                                    "value": f"%{words[0].group()}%"})
                    used.add(col)

        elif sym in SIMPLE:
            nums = sorted([n for n in numbers if n["position"] > pos and id(n) not in used_nums],
                          key=lambda n: n["position"])
            if nums:
                col = _nearest(nums[0]["position"], col_matches, allowed=numeric, exclude=used)
                if col and col not in used:
                    filters.append({"column": col, "operator": sym, "value": nums[0]["value"]})
                    used.add(col)
                    used_nums.add(id(nums[0]))

    group_by = None
    by = re.search(r"\bby\b", question, re.I)
    if by:
        cands = [c for c in col_matches if c["position"] >= by.end()]
        if cands:
            group_by = min(cands, key=lambda c: (c["position"], -c["score"]))["column"]

    order_by, order_dir, limit = None, "DESC", None
    top = TOP.search(question)
    bot = BOT.search(question)
    if top:
        limit = int(top.group(1))
        nc = [c for c in col_matches if c["column"] in numeric]
        if nc:
            order_by = min(nc, key=lambda c: (abs(c["position"] - top.end()), -c["score"]))["column"]
    elif bot:
        limit = int(bot.group(1))
        order_dir = "ASC"
        nc = [c for c in col_matches if c["column"] in numeric]
        if nc:
            order_by = min(nc, key=lambda c: (abs(c["position"] - bot.end()), -c["score"]))["column"]

    agg_col = None
    if intent in AGG:
        nc = [c for c in col_matches if c["column"] in numeric]
        if nc:
            agg_col = max(nc, key=lambda c: c["score"])["column"]

    return {"intent": intent, "filters": filters, "agg_column": agg_col,
            "group_by": group_by, "order_by": order_by, "order_dir": order_dir, "limit": limit}


def query_to_sql(query, table_name="data"):
    intent = query["intent"]
    filters = query["filters"]
    agg_col = query["agg_column"]
    group_by = query["group_by"]
    order_by = query["order_by"]
    order_dir = query["order_dir"]
    limit = query["limit"]
    tbl = _q(table_name)

    agg_overridden = limit is not None and group_by is None and intent in AGG
    if intent == "SELECT" or agg_overridden:
        select = "SELECT *"
    elif intent == "COUNT":
        select = f"SELECT {_q(group_by)}, COUNT(*)" if group_by else "SELECT COUNT(*)"
    elif intent in AGG:
        if not agg_col:
            raise ValueError(f"Could not detect which column to {intent}.")
        col = _q(agg_col)
        select = f"SELECT {_q(group_by)}, {intent}({col})" if group_by else f"SELECT {intent}({col})"
    else:
        select = "SELECT *"

    sql = f"{select} FROM {tbl}"

    if filters:
        parts = []
        for f in filters:
            col_q, op = _q(f["column"]), f["operator"]
            if op in NULL:
                parts.append(f"{col_q} {op}")
            elif op in BETWEEN:
                parts.append(f"{col_q} {op} {f['value']} AND {f['value2']}")
            else:
                val = str(f.get("value", ""))
                if val.replace(".", "", 1).lstrip("-").isdigit():
                    parts.append(f"{col_q} {op} {val}")
                else:
                    parts.append(f"{col_q} {op} '{val.replace(chr(39), chr(39)*2)}'")
        sql += " WHERE " + " AND ".join(parts)

    if group_by:
        sql += f" GROUP BY {_q(group_by)}"
    if order_by:
        sql += f" ORDER BY {_q(order_by)} {order_dir}"
    if limit:
        sql += f" LIMIT {limit}"

    return sql
