import os
import shutil

from openai import OpenAI
import re
from dotenv import load_dotenv
import random as rnd

# OpenAI API-Key initialisieren
load_dotenv()
api_key = os.getenv("secret_api_key_openai")
client = OpenAI(api_key=api_key)

# Fehlerkategorien mit Subfehlern definieren
error_num = rnd.uniform(1, 4)
errors = {
    "SyntaxError": [
        f"Erzeuge eine fehlerhafte Version, mit {error_num} zufälligen Fehlern, die einen Synatxfehler auslösen.",
        f"Erzeuge eine fehlerhafte Version, mit {error_num} zufälligen Fehlern, die einen Synatxfehler auslösen.",
        f"Erzeuge eine fehlerhafte Version, mit {error_num} zufälligen Fehlern, die einen Synatxfehler auslösen."
    ],
    "LogicError": [
        f"Erzeuge eine fehlerhafte Version, mit {error_num} zufälligen Fehlern, die einen Logikfehler auslösen.",
        f"Erzeuge eine fehlerhafte Version, mit {error_num} zufälligen Fehlern, die einen Logikfehler auslösen.",
        f"Erzeuge eine fehlerhafte Version, mit {error_num} zufälligen Fehlern, die einen Logikfehler auslösen."
    ],
    "RuntimeError": [
        f"Erzeuge eine fehlerhafte Version, mit {error_num} zufälligen Fehlern, die einen Laufzeitfehler auslösen.",
        f"Erzeuge eine fehlerhafte Version, mit {error_num} zufälligen Fehlern, die einen Laufzeitfehler auslösen.",
        f"Erzeuge eine fehlerhafte Version, mit {error_num} zufälligen Fehlern, die einen Laufzeitfehler auslösen."
    ]
}


# Hilfsfunktionen
def save_to_file(filename, content):
    """Speichert den gegebenen Inhalt in einer Datei."""
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)

def extract_code_blocks(content):
    """Extrahiert Python-Codeblöcke aus Markdown-formatiertem Text."""
    code_blocks = re.findall(r"```python(.*?)```", content, re.DOTALL)
    return [block.strip() for block in code_blocks]

# Verzeichnisse festlegen
initial_tasks_dir = "tasks/initial_tasks_bigcode"
error_tasks_dir = "tasks/error_tasks"

os.makedirs(error_tasks_dir, exist_ok=True)

# Funktion zur Generierung des fehlerhaften Codes
def generate_faulty_code(original_code, sub_error):
    """Generiert fehlerhaften Code basierend auf einer Subfehlerbeschreibung."""
    prompt = (f"Hier ist ein funktionierender Python-Code: \n\n{original_code}\n\n"
              f"{sub_error}\n"
              "Bitte füge basierend auf der Beschreibung gezielt Fehler hinzu. "
              "Erkläre außerhalb des Markdowns in max 20 Wörtern den Fehler kurz. Füge ansonsten keinerlei Kommentare ein."
              "Gib den fehlerhaften Code als Python-Codeblock im Markdown-Format zurück.")
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=1024
        )
        response_content = response.choices[0].message.content
        code_blocks = extract_code_blocks(response_content)
        return code_blocks[0] if code_blocks else None
    except Exception as e:
        print(f"Fehler bei der Generierung des fehlerhaften Codes: {e}")
        return None

# Hauptprozess: Für alle Task-Dateien
task_files = [f for f in os.listdir(initial_tasks_dir) if f.endswith(".py") and not f.endswith("_unittest.py")]
for task_file in task_files:
    task_path = os.path.join(initial_tasks_dir, task_file)
    with open(task_path, "r", encoding="utf-8") as file:
        original_code = file.read()

    # Generiere fehlerhaften Code für jede Subfehlerbeschreibung
    for error, sub_errors in errors.items():
        print(f"Bearbeite {error} für {task_file}...")
        for i, sub_error in enumerate(sub_errors, 1):
            faulty_code = generate_faulty_code(original_code, sub_error)
            if faulty_code:
                error_code_path = os.path.join(error_tasks_dir, f"{task_file.split('.')[0]}_{error.lower()}_suberror_{i}.py")
                save_to_file(error_code_path, faulty_code)
                print(f"Fehlerhafter Code für Subfehler {i} von {error} wurde gespeichert: {error_code_path}")
            else:
                print(f"Fehler bei der Generierung des fehlerhaften Codes für Subfehler {i} von {error}.")

# Kopieren der Unittest-Dateien ins Fehlerverzeichnis
unittest_files = [f for f in os.listdir(initial_tasks_dir) if f.endswith("_unittest.py")]
for unittest_file in unittest_files:
    source_path = os.path.join(initial_tasks_dir, unittest_file)
    destination_path = os.path.join(error_tasks_dir, unittest_file)
    shutil.copy(source_path, destination_path)
    print(f"Unittest-Datei {unittest_file} wurde nach {error_tasks_dir} kopiert.")
