import os
import shutil
import re
from openai import OpenAI
from dotenv import load_dotenv

# Lade die API-Schlüssel aus der .env-Datei
load_dotenv()

# Erstelle eine OpenAI-Instanz
client = OpenAI(
    api_key=os.getenv("secret_api_key_llama"),
    base_url="https://api.deepinfra.com/v1/openai",
)

# Verzeichnisse festlegen
initial_tasks_dir = "tasks/initial_tasks_bigcode"
error_tasks_dir = "tasks/error_tasks"

# Erstelle das Fehlerverzeichnis, falls es nicht existiert
os.makedirs(error_tasks_dir, exist_ok=True)

# Fehlerkategorie und Beschreibung zum Generieren des fehlerhaften Codes
errors = {
    "SyntaxError": "Füge einen Syntaxfehler in den folgenden Python-Code ein.",
    "LogicError": "Füge einen Logikfehler in den folgenden Python-Code ein. Die Änderungen sollten an Berechnungen, Bedingungen oder Datenflüssen durchgeführt werden. Der Code ist dadurch lauffähig, erzeugt aber falsche Ergebnisse.",
    "RuntimeError": "Füge einen Laufzeitfehler in den folgenden Python-Code ein."
}

# Hilfsfunktion zum Speichern von Inhalten in Dateien
def save_to_file(filename, content):
    """Speichert den gegebenen Inhalt in einer Datei."""
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)

# Hilfsfunktion zum Extrahieren von Python-Codeblöcken aus Markdown-Text
def extract_code_blocks(content):
    code_blocks = re.findall(r"```python(.*?)```", content, re.DOTALL)
    return [block.strip() for block in code_blocks]

# Hilfsfunktion zum Generieren des fehlerhaften Codes
def generate_faulty_code(original_code, error_description):
    prompt = (f"Hier ist ein funktionierender Python-Code:\n\n{original_code}\n\n"
              f"{error_description} "
              "Der Fehler muss innerhalb der bestehenden task_func implementiert werden."
              "Zeige am Ende des Python-Codes die Position des Fehlers an."
              "Benenne außerdem die Subkategorie des Fehlers (z. B. fehlende Klammer, Syntaxfehler, falscher Variablentyp, etc.)."
              "Füge abgesehen von diesen Kommentaren keinerlei Kommentare ein."
              "Gib den fehlerhaften Code als Python-Codeblock im Markdown-Format zurück.")

    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
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

# Hauptprozess
task_files = [f for f in os.listdir(initial_tasks_dir) if f.endswith(".py") and not f.endswith("_unittest.py")]

for task_file in task_files:
    task_path = os.path.join(initial_tasks_dir, task_file)
    with open(task_path, "r", encoding="utf-8") as file:
        original_code = file.read()

    # Funktionsaufruf zum Generieren und speichern des fehlerhaften Codes für jede Fehlerkategorie
    for error_name, error_description in errors.items():
        print(f"Bearbeite {error_name} für {task_file}...")
        faulty_code = generate_faulty_code(original_code, error_description)
        if faulty_code:
            error_code_path = os.path.join(error_tasks_dir, f"{task_file.split('.')[0]}_{error_name.lower()}.py")
            save_to_file(error_code_path, faulty_code)
            print(f"Fehlerhafter Code für {error_name} wurde gespeichert: {error_code_path}")
        else:
            print(f"Fehler bei der Generierung des fehlerhaften Codes für {error_name}.")

# Kopieren der Unittest-Dateien ins Fehlerverzeichnis
unittest_files = [f for f in os.listdir(initial_tasks_dir) if f.endswith("_unittest.py")]
for unittest_file in unittest_files:
    source_path = os.path.join(initial_tasks_dir, unittest_file)
    destination_path = os.path.join(error_tasks_dir, unittest_file)
    shutil.copy(source_path, destination_path)
    print(f"Unittest-Datei {unittest_file} wurde nach {error_tasks_dir} kopiert.")
