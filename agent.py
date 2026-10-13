import ollama

MODEL = "qwen2.5-coder:7b-instruct"

SYSTEM_PROMPT = "Du er en hjælpsom assistent. Svar kort og på dansk."


def load_model():
    ollama.generate(model=MODEL, prompt="", keep_alive="30m")


def ask(prompt):
    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    return response["message"]["content"]


if __name__ == "__main__":
    load_model()
    print(ask("hej"))