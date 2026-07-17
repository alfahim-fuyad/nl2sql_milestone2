def read_schema(df):
    schema = {}
    for col in df.columns:
        schema[col] = {
            "dtype": str(df[col].dtype),
            "sample_values": df[col].dropna().unique()[:100].tolist(),
        }
    return schema


def get_numeric_columns(schema):
    return [c for c, info in schema.items()
            if "int" in info["dtype"] or "float" in info["dtype"]]


def get_text_columns(schema):
    return [c for c, info in schema.items()
            if info["dtype"] in ("object", "str", "string", "category")]
