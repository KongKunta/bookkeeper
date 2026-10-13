import sqlite3
from pathlib import Path

import pandas as pd


def build_db(search_roots):
    db = sqlite3.connect("data.db")
    for root in search_roots:
        for f in Path(root).rglob("*.xlsx"):
            if f.name.startswith("~$"):
                continue
            sheets = pd.read_excel(f, sheet_name=None, dtype=str)
            pd.concat(sheets.values()).to_sql(f.stem.lower().replace(" ", "_"), db, if_exists="replace", index=False)
    db.close()


def search_excel(target):
    db = sqlite3.connect("data.db")
    db.row_factory = sqlite3.Row
    tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    for table in tables:
        for row in db.execute(f"SELECT * FROM {table}"):
            if target in tuple(row):
                db.close()
                return dict(row)
    db.close()
    return {"error": "No match"}


