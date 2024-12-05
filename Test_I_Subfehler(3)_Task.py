import os
from openai import OpenAI
import re
from dotenv import load_dotenv
import random as rnd

# OpenAI API-Key initialisieren
load_dotenv()
api_key = os.getenv("secret_api_key_openai")
client = OpenAI(api_key=api_key)

"""client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)"""


# Fehlerkategorien mit Subfehlern definieren
error_num = rnd.uniform(1,4)
errors = {
    "SyntaxError": [
        f"Erzeuge eine fehlerhafte Version, mit {error_num} zufälligen Syntaxfehlern.",
        f"Erzeuge eine fehlerhafte Version, mit {error_num} zufälligen Syntaxfehlern.",
        f"Erzeuge eine fehlerhafte Version, mit {error_num} zufälligen Syntaxfehlern."
    ],
    "LogicError": [
        f"Erzeuge eine fehlerhafte Version, mit {error_num} zufälligen Logikfehlern.",
        f"Erzeuge eine fehlerhafte Version, mit {error_num} zufälligen Logikfehlern.",
        f"Erzeuge eine fehlerhafte Version, mit {error_num} zufälligen Logikfehlern."
    ],
    "RuntimeError": [
        f"Erzeuge eine fehlerhafte Version, mit {error_num} zufälligen Laufzeitfehlern.",
        f"Erzeuge eine fehlerhafte Version, mit {error_num} zufälligen Laufzeitfehlern.",
        f"Erzeuge eine fehlerhafte Version, mit {error_num} zufälligen Laufzeitfehlern."
    ]
}



# Hilfsfunktionen
def save_to_file(filename, content):
    "Speichert den gegebenen Inhalt in einer Datei."
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)

def extract_code_blocks(content):
    "Extrahiert Python-Codeblöcke aus Markdown-formatiertem Text."
    code_blocks = re.findall(r"```python(.*?)```", content, re.DOTALL)
    return [block.strip() for block in code_blocks]

# Verzeichnisse festlegen
initial_tasks_dir = "tasks/initial_tasks"
error_tasks_dir = "tasks/error_tasks"

os.makedirs(error_tasks_dir, exist_ok=True)

# Funktion zur Generierung des fehlerhaften Codes
def generate_faulty_code(original_code, sub_error):
    "Generiert fehlerhaften Code basierend auf einer Subfehlerbeschreibung."
    prompt = (f"Hier ist ein funktionierender Python-Code: \n\n{original_code}\n\n"
              f"{sub_error}\n"
              "Überlege genau, der Fehler sollte zwingend auftreten und auch komplex zu identifizieren sein."
              f"Der Fehler muss innerhalb der bereits existierenden Funktion(en) integriert werden. Außerhalb dieser Funktion(en) darf nichts ergänzt werden.\n"
              "Gib den fehlerhaften Code als Python-Codeblock im Markdown-Format zurück. Es dürfen unter keinen Umständen Kommentare hinzugefügt werden, weder innerhalb noch außerhalb des Codes.")
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
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

# Funktion zur Generierung eines Unittests für alle Fehlerkategorien
def generate_unittest_for_all(original_code, faulty_files):
    "Generiert einen Unittest für alle fehlerhaften Codes in allen Kategorien."
    prompt = (
        f"Hier ist ein funktionierender Python-Code: \n\n{original_code}\n\n"
        f"Schreibe für diesen Code einen Unittest bestehend aus 20 Tesfällen, die für den bereitgestellten Code erfolgreich sein müssen."
        "Sieh dir jeden einzelnen Testfall genau an und überlege Schritt für Schritt warum dieser erfolgreicht ist für den bereitgestellten Code."
        f"Kapsle die Testfälle in einer Liste namens test_cases[].\n"
        "Gib den vollständigen Unittest als Python-Codeblock im Markdown-Format zurück.")
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=1024
        )
        response_content = response.choices[0].message.content
        code_blocks = extract_code_blocks(response_content)
        return code_blocks[0] if code_blocks else None
    except Exception as e:
        print(f"Fehler bei der Generierung des Unittests: {e}")
        return None

# Hauptprozess: Für alle Task-Dateien
task_files = [f for f in os.listdir(initial_tasks_dir) if f.endswith(".py")]
task_files= ["Task_01.py"]
for task_file in task_files:
    task_path = os.path.join(initial_tasks_dir, task_file)
    with open(task_path, "r", encoding="utf-8") as file:
        original_code = file.read()

    faulty_files = []

    # Generiere fehlerhaften Code für jede Subfehlerbeschreibung
    for error, sub_errors in errors.items():
        print(f"Bearbeite {error} für {task_file}...")
        for i, sub_error in enumerate(sub_errors, 1):
            faulty_code = generate_faulty_code(original_code, sub_error)
            if faulty_code:
                error_code_path = os.path.join(error_tasks_dir, f"{task_file.split('.')[0]}_{error.lower()}_suberror_{i}.py")
                save_to_file(error_code_path, faulty_code)
                faulty_files.append(error_code_path)
                print(f"Fehlerhafter Code für Subfehler {i} von {error} wurde gespeichert: {error_code_path}")
            else:
                print(f"Fehler bei der Generierung des fehlerhaften Codes für Subfehler {i} von {error}.")
                continue

    # Generiere Unittest für alle Fehlerkategorien
    if faulty_files:
        unittest_code = generate_unittest_for_all(original_code, faulty_files)
        if unittest_code:
            unittest_path = os.path.join(error_tasks_dir, f"{task_file.split('.')[0]}_unittest.py")
            save_to_file(unittest_path, unittest_code)
            print(f"Unittest für {task_file} wurde gespeichert: {unittest_path}")
        else:
            print(f"Fehler bei der Generierung des Unittests für {task_file}.")
