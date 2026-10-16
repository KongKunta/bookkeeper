import json

import ollama

import db
import utils
import vectordb
import os

from dotenv import load_dotenv

MAX_ROUNDS = 5

load_dotenv()
MODEL = os.getenv("MODEL")

SYSTEM_PROMPT = """Du er en hjælpsom assistent. Svar kort og på dansk.

Du har adgang til to slags viden:

1. Databasen (search_db) indeholder kundedata og flytteskemaet.
   - Kundedata: CVR-, kunde-, EAN- og ordrenumre.
   - Flytteskemaet: én række pr. dato. Kolonnen "Dato" er den dag, henvendelsen sker.
     Kolonnen "Fraflytning" er den tidligste fraflytningsdato, og kolonnen "Tilflytning" er den tidligste tilflytningsdato.

2. Guiderne (search_vectordb) beskriver, hvordan man gør ting i CRM:
   - Guide - Opret bruger i CRM
   - Guide - Meld fraflytning i CRM
   - Guide - Fejlmeld CRM til support

Sådan vælger du værktøj:
- Indeholder spørgsmålet en dato eller et nummer, så brug search_db med værdien. Datoer skrives som dd.mm.yyyy, fx 13.10.2026.
- Spørger brugeren om, hvordan man gør noget i CRM, eller om en fejl, så brug search_vectordb.
- Har du brug for begge dele, så brug begge.

Regler:
- search_db kan returnere flere rækker. Brug rækken, hvor "matched_column" er den kolonne, spørgsmålet handler om, fx "Dato" for dagen henvendelsen sker.
- Aflæs svaret direkte fra den række. Regn aldrig selv datoer ud.
- Opfind aldrig datoer, CVR-, kunde-, EAN- eller ordrenumre.
- Nævn, om svaret kommer fra flytteskemaet eller fra en guide.
- Finder du ikke svaret, så sig det, i stedet for at gætte."""

TOOLS = {
    "search": utils.search,
    "open": utils.open,
    "close": utils.close,
    "search_db": db.search_db,
    "search_vectordb": vectordb.search_vectordb,
    "build_db": db.build_db,
    "build_pdf_db": db.build_pdf_db,
}


def load_model():
    ollama.generate(model=MODEL, prompt="", keep_alive="30m")


def ask(prompt):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
    for _ in range(MAX_ROUNDS):
        response = ollama.chat(model=MODEL, messages=messages, tools=list(TOOLS.values()))
        message = response["message"]
        calls = [c["function"] for c in message.get("tool_calls") or []]

        if not calls:
            try:
                content = message["content"]
                call = json.loads(content[content.find("{"):content.rfind("}") + 1])
                name = call.get("name") or call.get("tool")
                if name in TOOLS:
                    calls = [{"name": name, "arguments": call.get("arguments", {})}]
            except (json.JSONDecodeError, AttributeError):
                pass

        if not calls:
            return message["content"]

        messages.append(message)
        for call in calls:
            result = TOOLS[call["name"]](**call["arguments"])
            messages.append({"role": "tool", "content": str(result)})

    return ollama.chat(model=MODEL, messages=messages)["message"]["content"]


if __name__ == "__main__":
    load_model()
    print(ask("Hvilken dato kan jeg tidligst tilflyt en kunde? I dag er dato 13.10.2026."))