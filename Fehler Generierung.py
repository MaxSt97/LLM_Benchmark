import os
from openai import OpenAI
import re
from dotenv import load_dotenv

# OpenAI API-Key initialisieren
load_dotenv()
api_key = os.getenv("secret_api_key_openai")
client = OpenAI(api_key=api_key)

# Fehlerkategorien definieren
errors = {
    "SyntaxError": "Erzeuge einen Syntaxfehler, der bei der Ausführung des Codes direkt einen Fehler auslöst.",
    "LogicError": "Erzeuge einen Logikfehler, der falsche Ergebnisse liefert, ohne einen direkten Fehler auszulösen.",
    "RuntimeError": "Erzeuge einen Laufzeitfehler. Beispielsweise: Division durch Null"
    "Zugriff auf nicht existierende Indizes in einer Liste,"
    "Nutzung von nicht definierten Variablen,Typfehler, z. B. Addition eines Strings zu einer Zahl"}

# Anzahl der Testfälle für den Unittest
num_testcase_unittest = 30

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
initial_tasks_dir = "tasks/initial_tasks_leetcode"
error_tasks_dir = "tasks/error_tasks"

os.makedirs(error_tasks_dir, exist_ok=True)

# Funktion zur Generierung des fehlerhaften Codes
def generate_faulty_code(original_code, error_type, description):
    "Generiert fehlerhaften Code basierend auf einer Fehlerbeschreibung."
    prompt = (f"Hier ist ein funktionierender Python-Code: \n\n{original_code}\n\n"
              f"{description}\n"
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

# Funktion zur Generierung von Unittests
def generate_unittest(original_code, faulty_code, error_file):
    "Generiert Unittests für den gegebenen fehlerhaften Code."
    module_name = os.path.splitext(os.path.basename(error_file))[0]
    prompt = (
        f"Hier ist ein funktionierender Python-Code: \n\n{original_code}\n\n"
        f"Schreibe für diesen Code einen Unittest bestehend aus {num_testcase_unittest} Tesfällen, die für den bereitgestellten Code erfolgreich sein müssen."
        "Sieh dir jeden einzelnen Testfall genau an und überlege Schritt für Schritt warum dieser erfolgreicht ist für den bereitgestellten Code."
        f"Die fehlerhafte Lösung ist in der Datei {module_name}.py gespeichert und enthält eine Klasse namens Solution. Importiere in deinem Unittest nur die Solution-Klasse aus dieser Datei.\n"
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

# Hauptprozess
task_files = [f for f in os.listdir(initial_tasks_dir) if f.endswith(".py")]
task_files=["Task_30.py"]
for task_file in task_files:
    task_path = os.path.join(initial_tasks_dir, task_file)
    with open(task_path, "r", encoding="utf-8") as file:
        original_code = file.read()

    for error, description in errors.items():
        print(f"Bearbeite {error} für Aufgabe {task_file}...")

        # Fehlerhaften Code generieren
        faulty_code = generate_faulty_code(original_code, error, description)
        if faulty_code:
            error_type = error.replace(" ", "_").lower()
            error_code_path = os.path.join(error_tasks_dir, f"{task_file.split('.')[0]}_{error_type}.py")
            save_to_file(error_code_path, faulty_code)
            print(f"Fehlerhafter Code für {error} wurde gespeichert: {error_code_path}")
        else:
            print(f"Fehler bei der Generierung des fehlerhaften Codes für {error}.")
            continue

        # Unittest generieren
        unittest_code = generate_unittest(original_code, faulty_code, error_code_path)
        if unittest_code:
            unittest_path = os.path.join(error_tasks_dir, f"{task_file.split('.')[0]}_{error_type}_unittest.py")
            save_to_file(unittest_path, unittest_code)
            print(f"Unittest für {error} wurde gespeichert: {unittest_path}")
        else:
            print(f"Fehler bei der Generierung des Unittests für {error}.")
