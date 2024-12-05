import os
from openai import OpenAI
from dotenv import load_dotenv
import re
import subprocess

# OpenAI API-Key initialisieren
load_dotenv()
api_key = os.getenv("secret_api_key_openai")
client = OpenAI(api_key=api_key)

"""#
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)"""

# Verzeichnis mit Fehlerdateien
error_tasks_directory = "tasks/error_tasks"

def get_error_files(directory):
    """Liste alle Dateien im angegebenen Verzeichnis, die nicht auf unittest.py enden."""
    try:
        return [
            os.path.join(directory, file)
            for file in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, file)) and not file.endswith("unittest.py")
        ]
    except Exception as e:
        print(f"Fehler beim Lesen des Verzeichnisses: {e}")
        return []

def read_file_content(file_path):
    """Lese den Inhalt einer Datei."""
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        print(f"Fehler beim Lesen der Datei {file_path}: {e}")
        return None

def analyze_error_with_openai(error_text):
    """Analysiere den Fehlertext mit OpenAI."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0,
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": f"Bitte analysiere den folgenden fehlerhaften Code und korrigiere ihn: {error_text}.\n"
                           "Überlege genau, welche(r) Aspekt Fehler auslösen könnte(n)."
                           f"Gib den korrigierten Code als Python-Codeblock im Markdown-Format zurück."
            }]
        )
        response_content = response.choices[0].message.content
        code_blocks = extract_code_blocks(response_content)
        return code_blocks[0] if code_blocks else None
    except Exception as e:
        print(f"Fehler bei der Kommunikation mit der OpenAI API: {e}")
        return None

def extract_code_blocks(content):
    "Extrahiert Python-Codeblöcke aus Markdown-formatiertem Text."
    code_blocks = re.findall(r"```python(.*?)```", content, re.DOTALL)
    return [block.strip() for block in code_blocks]

def save_to_file(filename, content):
    """Speichert den gegebenen Inhalt in einer Datei."""
    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(content)
    except Exception as e:
        print(f"Fehler beim Speichern der Datei {filename}: {e}")

def run_unittest(unittest_file, temp_file_path):
    """Führt den Unittest aus und gibt das Ergebnis zurück."""
    try:
        unittest_code = read_file_content(unittest_file)
        if not unittest_code:
            print(f"Unittest-Datei {unittest_file} konnte nicht gelesen werden.")
            return False

        # Namen des Moduls aus temp_file_path extrahieren
        temp_module_name = os.path.splitext(os.path.basename(temp_file_path))[0]

        # Prüfen, ob ein Import der Solution-Klasse vorhanden ist
        if "import Solution" not in unittest_code and "from" not in unittest_code:
            # Dynamischen Import zur Datei hinzufügen
            unittest_code = f"from {temp_module_name} import Solution\n\n" + unittest_code

        # Temporäre Unittest-Datei erstellen
        temp_unittest_path = unittest_file.replace(".py", "_temp.py")
        save_to_file(temp_unittest_path, unittest_code)

        # Unittest ausführen
        result = subprocess.run(["python", temp_unittest_path], capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Fehler beim Ausführen des Unittests: {e}")
        return False

def main():
    error_files = get_error_files(error_tasks_directory)
    if not error_files:
        print("Keine Fehlerdateien gefunden.")
        return

    # Initialisiere Zähler
    total_tests = 0
    successful_tests = 0
    failed_tests = 0

    for file_path in error_files:
        print(f"Analysiere Datei: {file_path}")
        error_content = read_file_content(file_path)
        if error_content:
            analysis = analyze_error_with_openai(error_content)
            if analysis:
                # Temporäre Datei mit korrigiertem Code erstellen
                temp_file_path = file_path.replace(".py", "_temp.py")
                save_to_file(temp_file_path, analysis)
                print(f"Korrigierter Code wurde gespeichert: {temp_file_path}")

                # Unittest-Datei für die gesamte Task bestimmen
                base_name = os.path.basename(file_path)  # Beispiel: Task_01_logicerror_suberror_1.py
                task_name = "_".join(base_name.split("_")[:2])  # Beispiel: Task_01
                unittest_file = os.path.join(error_tasks_directory, f"{task_name}_unittest.py")

                if os.path.exists(unittest_file):
                    print(f"Führe Unittest für {temp_file_path} aus...")
                    success = run_unittest(unittest_file, temp_file_path)

                    # Zähler erhöhen
                    total_tests += 1
                    if success:
                        print("Unittest erfolgreich bestanden!")
                        successful_tests += 1
                    else:
                        print("Unittest fehlgeschlagen!")
                        failed_tests += 1
                else:
                    print(f"Kein Unittest für {task_name} gefunden.")
            else:
                print("Keine Analyse erhalten.\n")
        else:
            print("Fehler konnte nicht gelesen werden.\n")

    # Ergebnisse ausgeben
    print(f"\nGesamtzahl der ausgeführten Tests: {total_tests}")
    print(f"Erfolgreiche Tests: {successful_tests}")
    print(f"Fehlgeschlagene Tests: {failed_tests}")

    if total_tests > 0:
        success_rate = (successful_tests / total_tests) * 100
        print(f"Erfolgsquote: {success_rate:.2f}%")
    else:
        print("Keine Tests ausgeführt.")

if __name__ == "__main__":
    main()

