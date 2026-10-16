import json

import ollama

import db
import utils
import vectordb

MAX_ROUNDS = 5
MODEL = "qwen2.5:7b-instruct"

SYSTEM_PROMPT = """Du er en hjælpsom assistent. Svar kort og på dansk.

Du har adgang til disse interne guides:
- Guide - Opret bruger i CRM: sådan oprettes en ny kunde, med CVR-, EAN- og kundenummer.
- Guide - Meld fraflytning i CRM: sådan registreres en fraflytning, annulleres ordrer og fortrydes en fraflytning.
- Guide - Fejlmeld CRM til support: hvad du skal prøve først, og hvordan en fejl meldes til support med den rigtige prioritet.

Du har adgang til disse værktøjer:
- search_vectordb(query): søger i de interne guides og returnerer de mest relevante afsnit. Brug den ved spørgsmål om, hvordan man gør noget, eller når noget ikke virker.
- search_db(target): slår en værdi op i databasen, fx et CVR-, kunde-, EAN- eller ordrenummer eller en dato, og returnerer hele rækken.
- search(root, pattern): finder filer i en mappe og dens undermapper, fx pattern="*.xlsx".
- open(path): åbner en fil på computeren.
- close(path): lukker vinduet med en åben fil.
- build_db(search_roots): importerer alle Excel-filer fra en liste af mapper til databasen.
- build_pdf_db(search_roots): importerer tabeller fra alle PDF-filer fra en liste af mapper til databasen.

Regler:
- Ved spørgsmål om, hvordan man gør noget, eller om fejl, skal du altid søge i guiderne med search_vectordb, før du svarer.
- Svar ud fra guiderne, og nævn hvilken guide svaret kommer fra.
- Spørg kun brugeren om flere oplysninger, hvis ingen guide dækker spørgsmålet.
- Opfind aldrig CVR-, kunde-, EAN- eller ordrenumre. Slå dem op med search_db."""

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
                call = json.loads(message["content"])
                if call.get("name") in TOOLS:
                    calls = [call]
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
    print(ask("CRM virker ikke, hvad skal jeg gøre?"))