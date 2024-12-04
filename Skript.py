import os
import re
from openai import OpenAI
from dotenv import load_dotenv

# OpenAI API-Key initialisieren
load_dotenv()
api_key = os.getenv("secret_api_key_openai")
client = OpenAI(api_key=api_key)

# Anzahl der Testfälle für den Unittest als Konstante definieren
num_test_case = 30

def save_to_file(filename, content):
    """Speichert den gegebenen Inhalt in einer Datei."""
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)

def extract_code_blocks(content):
    """Extrahiert Codeblöcke aus Markdown-formatiertem Text."""
    code_blocks = re.findall(r"```(?:python)?\n(.*?)```", content, re.DOTALL)
    return [block.strip() for block in code_blocks]

def generate_faulty_code(original_code, description):
    """Generiert fehlerhaften Code basierend auf einer Fehlerbeschreibung."""
    prompt = (
        f"Hier ist ein funktionierender Python-Code:\n\n{original_code}\n\n"
        f"{description}\n"
        "Überlege genau, der Fehler sollte zwingend auftreten und auch komplex zu identifizieren sein. "
        "Der Fehler muss innerhalb der bereits existierenden Funktion(en) integriert werden. "
        "Außerhalb dieser Funktion(en) darf nichts ergänzt werden.\n"
        "Gib den fehlerhaften Code als Python-Codeblock im Markdown-Format zurück. "
        "Es dürfen unter keinen Umständen Kommentare hinzugefügt werden, weder innerhalb noch außerhalb des Codes."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=1024
        )
        response_content = response.choices[0].message.content
        code_blocks = extract_code_blocks(response_content)
        return code_blocks[0] if code_blocks else None
    except Exception as e:
        print(f"Fehler bei der Generierung des fehlerhaften Codes: {e}")
        return None

def generate_unittest(original_code, num_test_cases):
    """Generiert Unittests für den gegebenen Code."""
    prompt = (
        f"Hier ist ein funktionierender Python-Code:\n\n{original_code}\n\n"
        f"Schreibe für diesen Code einen Unittest bestehend aus {num_test_cases} Testfällen, die für den bereitgestellten Code erfolgreich sein müssen. "
        "Sieh dir jeden einzelnen Testfall genau an und überlege Schritt für Schritt, warum dieser erfolgreich ist für den bereitgestellten Code. "
        "Kapsle die Testfälle in einer Liste namens test_cases.\n"
        "Gib den vollständigen Unittest als Python-Codeblock im Markdown-Format zurück."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=2048  # Erhöht, um genug Platz für den Unittest zu haben
        )
        response_content = response.choices[0].message.content
        code_blocks = extract_code_blocks(response_content)
        return code_blocks[0] if code_blocks else None
    except Exception as e:
        print(f"Fehler bei der Generierung des Unittests: {e}")
        return None

def main():
    """Hauptfunktion des Skripts."""
    # Fehlerkategorien definieren
    errors = {
        "SyntaxError": "Erzeuge einen Syntaxfehler, der bei der Ausführung des Codes direkt einen Fehler auslöst.",
        "LogicError": "Erzeuge einen Logikfehler, der falsche Ergebnisse liefert, ohne einen direkten Fehler auszulösen.",
        "RuntimeError": (
            "Erzeuge einen Laufzeitfehler. Beispielsweise: Division durch Null, "
            "Zugriff auf nicht existierende Indizes in einer Liste, "
            "Nutzung von nicht definierten Variablen, Typfehler, z. B. Addition eines Strings zu einer Zahl."
        )
    }

    # Verzeichnisse festlegen
    initial_tasks_dir = "tasks/initial_tasks"
    error_tasks_dir = "tasks/error_tasks"

    os.makedirs(error_tasks_dir, exist_ok=True)

    # Alle Task-Dateien im Verzeichnis initial_tasks_dir finden
    task_files = [f for f in os.listdir(initial_tasks_dir) if f.endswith(".py")]
    task_files = ["Task_01.py"]  # Falls Sie nur bestimmte Dateien verarbeiten möchten

    for task_file in task_files:
        task_path = os.path.join(initial_tasks_dir, task_file)
        with open(task_path, "r", encoding="utf-8") as file:
            original_code = file.read()

        # Unittest nur einmal generieren
        unittest_code = generate_unittest(original_code, num_test_case)
        if unittest_code:
            # Unittest für jede Fehlerkategorie abspeichern
            for error in errors.keys():
                error_type = error.replace(" ", "_").lower()
                unittest_filename = f"{os.path.splitext(task_file)[0]}_{error_type}_unittest.py"
                unittest_path = os.path.join(error_tasks_dir, unittest_filename)
                save_to_file(unittest_path, unittest_code)
                print(f"Unittest wurde gespeichert: {unittest_path}")
        else:
            print(f"Fehler bei der Generierung des Unittests für {task_file}.")
            continue  # Falls der Unittest nicht generiert werden konnte, überspringe diese Datei

        # Fehlerhaften Code für jede Fehlerkategorie generieren
        for error, description in errors.items():
            print(f"Bearbeite {error} für Aufgabe {task_file}...")

            faulty_code = generate_faulty_code(original_code, description)
            if faulty_code:
                error_type = error.replace(" ", "_").lower()
                error_code_filename = f"{os.path.splitext(task_file)[0]}_{error_type}.py"
                error_code_path = os.path.join(error_tasks_dir, error_code_filename)
                save_to_file(error_code_path, faulty_code)
                print(f"Fehlerhafter Code für {error} wurde gespeichert: {error_code_path}")
            else:
                print(f"Fehler bei der Generierung des fehlerhaften Codes für {error}.")

if __name__ == "__main__":
    main()
