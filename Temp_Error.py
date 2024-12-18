import os
import shutil
import re
from openai import OpenAI
from dotenv import load_dotenv

# OpenAI API-Key initialisieren
load_dotenv()
client = OpenAI(
    api_key=os.getenv("secret_api_key_llama"),
    base_url="https://api.deepinfra.com/v1/openai",
)

# Verzeichnisse festlegen
initial_tasks_dir = "tasks/initial_tasks_bigcode"
error_tasks_dir = "tasks/error_tasks"

os.makedirs(error_tasks_dir, exist_ok=True)

# Fehlerkategorien
errors = {
    "SyntaxError": "Füge einen Syntaxfehler in den folgenden Python-Code ein.",
    "LogicError": "Füge einen Logikfehler in den folgenden Python-Code ein. Die Änderungen sollten an Berechnungen, Bedingungen oder Datenflüssen durchgeführt werden. Der Code ist dadurch lauffähig, erzeugt aber falsche Ergebnisse.",
    "RuntimeError": "Füge einen Laufzeitfehler in den folgenden Python-Code ein."
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


def generate_faulty_code(original_code, error_description, unittest_code=None):
    """Generiert fehlerhaften Code basierend auf der Fehlerbeschreibung und ggf. einem Unittest."""
    prompt = (f"Hier ist ein funktionierender Python-Code:\n\n{original_code}\n\n"
              f"{error_description} "
              "Der Fehler muss innerhalb der bestehenden task_func eingefügt werden. "
              "Erkläre den Fehler innerhalb des Markdowns am Ende des Python-Codes kurz in Form eines Kommentars. "
              "Füge ansonsten keinerlei Kommentare innerhalb des Python-Codes hinzu.")

    if unittest_code:
        prompt += ("\n\nZusätzlich hier der zugehörige Unittest:\n\n"
                   f"{unittest_code}\n\n"
                   "Der generierte Fehler sollte dazu führen, dass dieser Unittest fehlschlägt."
                   "Der Unittest darf im Markdown selbst nicht auftauchen.")

    prompt += "\n\nGib den fehlerhaften Code als Python-Codeblock im Markdown-Format zurück. "

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

    # Passenden Unittest laden, falls vorhanden
    unittest_file = f"{task_file.split('.')[0]}_unittest.py"
    unittest_code = None
    unittest_path = os.path.join(initial_tasks_dir, unittest_file)
    if os.path.exists(unittest_path):
        with open(unittest_path, "r", encoding="utf-8") as unittest_file:
            unittest_code = unittest_file.read()

    # Generiere fehlerhaften Code für jede Fehlerkategorie
    for error_name, error_description in errors.items():
        print(f"Bearbeite {error_name} für {task_file}...")
        faulty_code = generate_faulty_code(original_code, error_description, unittest_code)
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
