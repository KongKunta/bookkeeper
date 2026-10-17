import sqlite3
from pathlib import Path

import pandas as pd
import pdfplumber


def build_db(search_roots: list[str]):
    """Importér alle Excel-filer fra mapperne til databasen. Bruges kun, når databasen skal opdateres.

    Args:
        search_roots: Liste af mapper, der søges i, fx ["C:/Users/navn/Documents"].
    """
    db = sqlite3.connect("data.db")
    for root in search_roots:
        for f in Path(root).rglob("*.xlsx"):
            if f.name.startswith("~$"):
                continue
            sheets = pd.read_excel(f, sheet_name=None, dtype=str)
            pd.concat(sheets.values()).to_sql(f.stem.lower().replace(" ", "_"), db, if_exists="replace", index=False)
    db.close()


def build_pdf_db(search_roots: list[str]):
    """Importér tabeller fra alle PDF-filer i mapperne til databasen. Bruges kun, når databasen skal opdateres.

    Args:
        search_roots: Liste af mapper, der søges i, fx ["C:/Users/navn/Documents"].
    """
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
    """Slå en værdi op i databasen med kundedata og skemaer, fx flytteskemaet, og returnér alle rækker, hvor værdien findes.
    Hver række har feltet "matched_column", der viser hvilken kolonne værdien stod i.
    Står værdien i en tabels første kolonne, fx "Dato" eller "CVR", returneres kun de rækker.
    Brug den, når spørgsmålet indeholder et CVR-, kunde-, EAN- eller ordrenummer eller en dato.

    Args:
        target: Værdien der søges efter. CVR-nummer (8 cifre), kundenummer (9 cifre),
            EAN-nummer (13 cifre), ordrenummer (5 cifre) eller en dato skrevet som dd.mm.yyyy, fx 13.10.2026.
    """
    db = sqlite3.connect("data.db")
    db.row_factory = sqlite3.Row
    tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    key_matches = []
    matches = []
    for table in tables:
        for row in db.execute(f'SELECT * FROM "{table}"'):
            for column in row.keys():
                if row[column] and str(target) in str(row[column]).split():
                    match = {"matched_column": column, **dict(row)}
                    if column == row.keys()[0]:
                        key_matches.append(match)
                    matches.append(match)
    db.close()
    return key_matches or matches or [{"error": "No match"}]




if __name__ == "__main__":
    build_pdf_db(["./tester"])
    build_db(["./tester"])