import sqlite3
from pathlib import Path

import pandas as pd
import pdfplumber


def build_db(search_roots):
    db = sqlite3.connect("data.db")
    for root in search_roots:
        for f in Path(root).rglob("*.xlsx"):
            if f.name.startswith("~$"):
                continue
            sheets = pd.read_excel(f, sheet_name=None, dtype=str)
            pd.concat(sheets.values()).to_sql(f.stem.lower().replace(" ", "_"), db, if_exists="replace", index=False)
    db.close()


def build_pdf_db(search_roots):
    db = sqlite3.connect("data.db")
    for root in search_roots:
        for f in Path(root).rglob("*.pdf"):
            with pdfplumber.open(f) as pdf:
                tables = [t for page in pdf.pages for t in page.extract_tables()]
            if not tables:
                continue
            frames = []
            for t in tables:
                columns = [str(c or f"col_{i}").replace("\x00", "").replace("\n", " ") for i, c in enumerate(t[0])]
                frames.append(pd.DataFrame(t[1:], columns=columns))
            df = pd.concat(frames)
            df.to_sql(f.stem.lower().replace(" ", "_"), db, if_exists="replace", index=False)
    db.close()


def search_db(target):
    db = sqlite3.connect("data.db")
    db.row_factory = sqlite3.Row
    tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    for table in tables:
        for row in db.execute(f'SELECT * FROM "{table}"'):
            if any(str(target) in str(cell).split() for cell in row if cell):
                db.close()
                return dict(row)
    db.close()
    return {"error": "No match"}




if __name__ == "__main__":
    build_pdf_db(["./tester"])
    build_db(["./tester"])