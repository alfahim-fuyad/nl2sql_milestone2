import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "core"))

from dataset_loader  import load_dataset
from schema_reader   import read_schema
from intent_detector import load_model, predict_intent
from sql_generator   import build_query, query_to_sql
from sql_validator   import validate_sql
from sql_executor    import execute_query


def print_table(columns, rows):
    if not rows:
        print("No results.")
        return
    widths = [max(len(str(c)), max(len(str(r[i])) for r in rows))
              for i, c in enumerate(columns)]
    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    row_fmt = "|" + "|".join(f" {{:<{w}}} " for w in widths) + "|"
    print(sep)
    print(row_fmt.format(*columns))
    print(sep)
    for row in rows:
        print(row_fmt.format(*[str(v) for v in row]))
    print(sep)
    print(f"{len(rows)} row(s)")


def run(question, schema, model, vectorizer, db_path, table_name):
    intent = predict_intent(question, model, vectorizer)
    print(f"Intent : {intent}")

    query = build_query(question, schema, intent)
    try:
        sql = query_to_sql(query, table_name)
    except ValueError as e:
        print(f"Error: {e}")
        return
    print(f"SQL    : {sql}\n")

    valid, msg = validate_sql(sql, schema, table_name)
    if not valid:
        print(f"Invalid: {msg}")
        return

    try:
        cols, rows = execute_query(sql, db_path)
    except Exception as e:
        print(f"Execute error: {e}")
        return

    print_table(cols, rows)


def main():
    print("=" * 50)
    print("  nl2sql-366  |  Natural Language to SQL")
    print("=" * 50)

    csv_path = input("\nCSV path (default: data/sample.csv): ").strip() or "data/sample.csv"
    db_path = "data/database.db"
    table_name = "data"

    try:
        df = load_dataset(csv_path, db_path, table_name)
    except FileNotFoundError as e:
        print(e)
        return

    schema = read_schema(df)
    print(f"Loaded: {len(df)} rows | Columns: {list(df.columns)}\n")

    try:
        model, vectorizer = load_model()
    except FileNotFoundError:
        print("Model not found. Run: python3 models/train_intent.py")
        return

    print("Ask a question in English. Type 'exit' to quit.\n")

    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not question:
            continue
        if question.lower() in ("exit", "quit"):
            break
        run(question, schema, model, vectorizer, db_path, table_name)
        print()


if __name__ == "__main__":
    main()
