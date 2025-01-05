import os
from openai import OpenAI
import re
from dotenv import load_dotenv
from datasets import load_dataset
import pandas as pd

# Lade die API-Schlüssel aus der .env-Datei
load_dotenv()

# Erstelle eine OpenAI-Instanz
client = OpenAI(
    api_key=os.getenv("secret_api_key_openai")
)

# Verzeichnisse festlegen
initial_tasks_dir = "tasks/initial_tasks_bigcode"
os.makedirs(initial_tasks_dir, exist_ok=True)  # Sicherstellen, dass das Basisverzeichnis existiert

# Hilfsfunktion zur Extraktion von Python-Codeblöcken
def extract_code_blocks(content):
    code_blocks = re.findall(r"```python(.*?)```", content, re.DOTALL)
    return [block.strip() for block in code_blocks]

# Hilfsfunktion zum Generieren von Code und Unit-Tests
def generate_code_and_tests(canonical_solution, test_prompt):
    prompt = (
        f"Hier ist eine Beschreibung eines funktionierenden Codes:\n\n"
        f"Canonical Solution:\n{canonical_solution}\n\n"
        f"Test Prompt:\n{test_prompt}\n\n"
        "Erstelle basierend auf diesen Informationen eine Python-Funktion und dazugehörige Unit-Tests. "
        "Gib beide als separate Python-Codeblöcke im Markdown-Format zurück. "
        "Der erste Codeblock sollte den funktionierenden Code enthalten, der zweite die Unit-Tests."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=1500
        )
        response_content = response.choices[0].message.content
        code_blocks = extract_code_blocks(response_content)
        return code_blocks if code_blocks else [None, None]
    except Exception as e:
        print(f"Fehler bei der Generierung des Codes: {e}")
        return [None, None]

# BigCodeBench-Dataset laden und in DataFrame umwandeln
ds = load_dataset("bigcode/bigcodebench-hard")
df = pd.DataFrame(ds['v0.1.0_hf'])

# Filtern von gültigen Tasks (mit vorhandenen 'canonical_solution' und 'test')
valid_tasks = df[(df['canonical_solution'].notna()) & (df['test'].notna())]

# Zufällige Auswahl von X gültigem Task
random_tasks = valid_tasks.sample("X")

# Hauptprozess
for _, row in random_tasks.iterrows():
    task_id = row["task_id"]
    task_id_cleaned = re.sub(r"[\\/]", "_", task_id)  # Pfadtrennzeichen bereinigen
    canonical_solution = row["canonical_solution"]
    test_prompt = row["test"]

    # Code und Tests generieren
    function_code, unittest_code = generate_code_and_tests(canonical_solution, test_prompt)

    # Code und Unit-Test speichern
    if function_code and unittest_code:
        function_file_path = os.path.join(initial_tasks_dir, f"Task_{task_id_cleaned}.py")
        with open(function_file_path, "w", encoding="utf-8") as function_file:
            function_file.write(function_code)

        unittest_file_path = os.path.join(initial_tasks_dir, f"Task_{task_id_cleaned}_unittest.py")
        with open(unittest_file_path, "w", encoding="utf-8") as unittest_file:
            unittest_file.write(unittest_code)

        print(f"Code und Unit-Test für Task {task_id_cleaned} erfolgreich gespeichert.")
    else:
        print(f"Fehler bei der Generierung von Code oder Unit-Test für Task {task_id_cleaned}.")

