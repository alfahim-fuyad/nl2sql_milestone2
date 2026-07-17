import re

DANGEROUS = ["drop", "delete", "update", "insert", "alter",
             "attach", "detach", "pragma", "create", "truncate"]


def _strip_literals(sql):
    return re.sub(r"'(?:[^']|'')*'", "''", sql)


def validate_sql(sql, schema, table_name="data"):
    s = sql.strip()
    if not s.lower().startswith("select"):
        return False, "Query must start with SELECT."

    clean = _strip_literals(s).lower()
    for kw in DANGEROUS:
        if re.search(r"\b" + kw + r"\b", clean):
            return False, f"Dangerous keyword: '{kw}'."

    if ";" in s.rstrip(";"):
        return False, "Multiple statements not allowed."

    pat = re.compile(
        r'\b(?:from|join)\s+(?:"' + re.escape(table_name.lower()) + r'"|'
        + re.escape(table_name.lower()) + r'\b)', re.I)
    if not pat.search(clean):
        return False, f"Table '{table_name}' not found."

    valid_cols = {c.lower() for c in schema}
    where = re.search(r"\bwhere\b(.+?)(?:\bgroup\s+by\b|\border\s+by\b|\blimit\b|$)",
                      s, re.I | re.DOTALL)
    if where:
        clause = _strip_literals(where.group(1))
        for m in re.finditer(
                r'(?:"([^"]+)"|`([^`]+)`|([A-Za-z_][A-Za-z0-9_ ]*))'
                r'\s*(?:=|!=|<>|>=|<=|>|<|\bLIKE\b|\bBETWEEN\b|\bIS\b)',
                clause, re.I):
            col = (m.group(1) or m.group(2) or m.group(3) or "").strip()
            if col and col.lower() not in ("and", "or", "not") and col.lower() not in valid_cols:
                return False, f"Column '{col}' not in schema."

    return True, "OK"
