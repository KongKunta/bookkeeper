import ollama

import db
import utils
import json

MODEL = "qwen2.5:7b-instruct"

SYSTEM_PROMPT = """Du er en hjælpsom assistent. Svar kort og på dansk.
Du har adgang til disse værktøjer:
- search(root, pattern): finder filer i en mappe og dens undermapper, fx pattern="*.xlsx".
- open(path): åbner en fil på computeren.
- close(path): lukker vinduet med en åben fil.
- search_db(target): slår en værdi op i databasen, fx et CVR-, kunde-, EAN- eller ordrenummer, og returnerer hele rækken.
- build_db(search_roots): importerer alle Excel-filer fra en liste af mapper til databasen.
- build_pdf_db(search_roots): importerer tabeller fra alle PDF-filer fra en liste af mapper til databasen.
Brug kun et værktøj, når det er nødvendigt for at svare."""

TOOLS = {
    "search": utils.search,
    "open": utils.open,
    "close": utils.close,
    "search_db": db.search_db,
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
    print(ask("hej, hvilket kundenummer tilhører cvr 28034063"))