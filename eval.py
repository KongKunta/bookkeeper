import csv
from datetime import datetime

import agent

TESTS = [
    # Tilflytning (flytteskema)
    ("Hvilken dato kan jeg tidligst tilflytte en kunde? I dag er d. 13.10.2026.", "05.10.2026"),
    ("Hvor langt tilbage kan en tilflytning registreres, hvis vi melder den 01.10.2026?", "23.09.2026"),
    ("Kunden ringede 06.10.2026. Hvad er første mulige tilflytningsdag?", "28.09.2026"),
    ("Tidligste indflytning ved henvendelse fredag 09.10.2026?", "01.10.2026"),
    ("Vi skriver 20.10.2026 i dag. Hvornår kan tilflytningen tidligst stå?", "12.10.2026"),
    ("Hvis en kunde vil flytte ind og vi har 27.10.2026, hvad er den tidligste dato?", "19.10.2026"),
    # Fraflytning (flytteskema)
    ("Hvornår kan kunden tidligst fraflytte, hvis de melder det 13.10.2026?", "22.10.2026"),
    ("En lejer opsiger 15.10.2026. Hvad er første fraflytningsdato?", "26.10.2026"),
    ("Tidligste udflytning ved henvendelse 24.10.2026?", "03.11.2026"),
    ("Kunden vil fraflytte. I dag er det 30.10.2026. Hvornår tidligst?", "10.11.2026"),
    ("Hvad er den tidligste fraflytning for en opsigelse modtaget 31.10.2026?", "10.11.2026"),
    ("Opsigelse kom ind 06.10.2026 – hvornår kan de tidligst være ude?", "15.10.2026"),
    # Kundedata
    ("Hvilket kundenummer har CVR 28034063?", "113208723"),
    ("Find EAN-nummeret for kunden med CVR 40703945.", "5798733267959"),
    ("Hvilket CVR hører til kundenummer 483100304?", "56399124"),
    ("Hvad er ordrenummeret for CVR 28034063?", "34015"),
    ("Kunden med CVR 50717432 ringer. Hvad er deres kundenummer?", "198356259"),
    ("Slå kundenummer 770876131 op og giv mig CVR-nummeret.", "78239848"),
    # Guides
    ("CRM virker ikke, hvad skal jeg gøre?", "support"),
    ("Hvordan opretter jeg en ny kunde i CRM?", "Ny kunde"),
]


def run(path=None):
    path = path or f"eval_{agent.MODEL.replace(':', '_')}_{datetime.now():%Y%m%d_%H%M}.csv"
    correct = 0
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["nr", "spørgsmål", "forventet", "korrekt", "svar"])
        for i, (question, expected) in enumerate(TESTS, 1):
            answer = agent.ask(question)
            ok = expected.lower() in answer.lower()
            correct += ok
            writer.writerow([i, question, expected, ok, answer])
            print(f"{i:2}/{len(TESTS)} {'OK ' if ok else 'FEJL'} {question}")
    print(f"\n{correct}/{len(TESTS)} korrekte – gemt i {path}")


if __name__ == "__main__":
    agent.load_model()
    run()