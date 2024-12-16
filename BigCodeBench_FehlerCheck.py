import os
import sys
import re
import subprocess
import importlib.util  # Für dynamischen Modul-Import
from openai import OpenAI
from dotenv import load_dotenv

# OpenAI API-Key initialisieren
load_dotenv()
api_key = os.getenv("secret_api_key_openai")
client = OpenAI(api_key=api_key)

# Verzeichnisse
error_tasks_directory = "tasks/error_tasks"

def get_error_files(directory):
    """Liste alle Python-Dateien im Verzeichnis auf, die nicht auf unittest.py enden."""
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
    """Analysiere den Fehlertext mit OpenAI und liefere die korrigierte Version zurück."""
    try:
        prompt = (
            f"Hier ist ein fehlerhafter Python-Code:\n\n{error_text}\n\n"
            "Analysiere die Fehler und gib eine korrigierte Version des Codes zurück. "
            "Behalte die Struktur des ursprünglichen Codes bei. "
            "Gib den korrigierten Code als Python-Codeblock im Markdown-Format zurück."
        )
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=1,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        response_content = response.choices[0].message.content
        code_blocks = extract_code_blocks(response_content)
        return code_blocks[0] if code_blocks else None
    except Exception as e:
        print(f"Fehler bei der Kommunikation mit der OpenAI API: {e}")
        return None

def extract_code_blocks(content):
    """Extrahiert Python-Codeblöcke aus Markdown-formatiertem Text."""
    code_blocks = re.findall(r"```python(.*?)```", content, re.DOTALL)
    return [block.strip() for block in code_blocks]

def save_to_file(filename, content):
    """Speichert den gegebenen Inhalt in einer Datei."""
    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(content)
    except Exception as e:
        print(f"Fehler beim Speichern der Datei {filename}: {e}")

def inject_module_import(unittest_file_path, module_name):
    """Fügt den Modulimport in die Unittest-Datei ein und entfernt nur relevante alte Importe."""
    try:
        unittest_code = read_file_content(unittest_file_path)
        if unittest_code is None:
            return False

        # Entferne nur Importe, die von Dateien mit `Task_..._corrected` stammen
        unittest_code = re.sub(r"from Task_.*_corrected import \*\n", "", unittest_code)

        # Prüfen, ob der neue Import bereits vorhanden ist
        import_statement = f"from {module_name} import *\n"
        if import_statement not in unittest_code:
            unittest_code = import_statement + unittest_code  # Füge neuen Import hinzu

            # Schreibe die Änderungen zurück in die Unittest-Datei
            with open(unittest_file_path, "w", encoding="utf-8") as file:
                file.write(unittest_code)
            print(f"Modul {module_name} wurde in {unittest_file_path} importiert.")
        else:
            print(f"Modul {module_name} ist bereits in {unittest_file_path} importiert.")

        return True
    except Exception as e:
        print(f"Fehler beim Importieren des Moduls in {unittest_file_path}: {e}")
        return False

def run_unittest(unittest_file, module_name, module_path):
    """Führt den Unittest aus und gibt das Ergebnis zurück."""
    try:
        # Dynamischer Import des korrigierten Moduls
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Unittest ausführen
        result = subprocess.run(["python", unittest_file], capture_output=True, text=True)
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

    # Verzeichnis zu sys.path hinzufügen
    sys.path.insert(0, error_tasks_directory)

    # Initialisiere Zähler
    total_tests = 0
    successful_tests = 0
    failed_tests = 0

    for file_path in error_files:
        print(f"Analysiere Datei: {file_path}")
        error_content = read_file_content(file_path)

        if error_content:
            # OpenAI API aufrufen, um die korrigierte Version zu erhalten
            corrected_code = analyze_error_with_openai(error_content)
            if corrected_code:
                # Erstelle die _corrected-Version
                corrected_file_path = file_path.replace(".py", "_corrected.py")
                save_to_file(corrected_file_path, corrected_code)
                print(f"Korrigierter Code wurde gespeichert: {corrected_file_path}")

                # Namen für das Unittest-File bestimmen
                base_name = os.path.basename(file_path).split("_")[0:3]  # Task_BigCodeBench_1085
                task_name = "_".join(base_name)
                unittest_file = os.path.join(error_tasks_directory, f"{task_name}_unittest.py")

                if os.path.exists(unittest_file):
                    # Modulimport in die Unittest-Datei einfügen
                    module_name = os.path.splitext(os.path.basename(corrected_file_path))[0]
                    inject_module_import(unittest_file, module_name)

                    print(f"Führe Unittest für {corrected_file_path} aus...")
                    success = run_unittest(unittest_file, module_name, corrected_file_path)

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
                print("Keine korrigierte Version erhalten.\n")
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
