import os
import sys
import re
import subprocess
import importlib.util
import shutil
from openai import OpenAI
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
import functools
import time

# Flush print
print = functools.partial(print, flush=True)

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


def analyze_error_with_openai(error_text, unittest_output=None):
    """Analysiere den Fehlertext (und optional die Fehlermeldung des Unittest) mit OpenAI."""
    try:
        prompt = (
            f"Hier ist ein fehlerhafter Python-Code:\n\n{error_text}\n\n"
            "Analysiere die Fehler und gib eine korrigierte Version des Codes zurück. "
            "Behalte die Struktur des ursprünglichen Codes bei."
        )
        if unittest_output:
            prompt += (
                f"\n\nHier ist die Fehlermeldung des zuletzt ausgeführten Unittests:\n\n{unittest_output}\n\n"
                "Berücksichtige diese Fehlermeldung bei der Korrektur."
            )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
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
        time.sleep(1)  # Warte kurz, um sicherzustellen, dass die Datei gespeichert ist
    except Exception as e:
        print(f"Fehler beim Speichern der Datei {filename}: {e}")


def inject_module_import(unittest_file_path, module_name):
    """Fügt den Modulimport in die Unittest-Datei ein."""
    try:
        unittest_code = read_file_content(unittest_file_path)
        if unittest_code is None:
            return False

        # Entferne alte Importe, die mit 'from Task_' beginnen
        unittest_code = re.sub(r"^from Task_.*\n", "", unittest_code, flags=re.MULTILINE)

        # Füge den neuen Import als absoluten Import hinzu
        import_statement = f"from {module_name} import *\n"
        if import_statement not in unittest_code:
            unittest_code = import_statement + unittest_code
            with open(unittest_file_path, "w", encoding="utf-8") as file:
                file.write(unittest_code)
        return True
    except Exception as e:
        print(f"Fehler beim Importieren des Moduls: {e}")
        return False


def run_unittest(unittest_file, module_name, module_path):
    try:
        # Warten, um sicherzustellen, dass die Datei korrekt gespeichert wurde
        time.sleep(1)

        # Modul laden
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Unittest ausführen
        unittest_dir = os.path.dirname(unittest_file)
        result = subprocess.run(
            ["python", os.path.basename(unittest_file)],
            capture_output=True, text=True, cwd=unittest_dir
        )
        output = result.stdout + result.stderr

        # Prüfe den Rückgabewert des Prozesses
        success = result.returncode == 0
        return success, output
    except Exception as e:
        print(f"Fehler beim Ausführen des Unittests: {e}")
        return False, str(e)


def process_file(file_path, iteration_stats):
    """Verarbeitet eine Datei mit maximal drei Iterationen."""
    error_content = read_file_content(file_path)
    if not error_content:
        return file_path, False, "Keine Inhalte"

    corrected_code = None
    corrected_file_path = file_path.replace(".py", "_corrected.py")
    base_name = os.path.basename(file_path).split("_")[0:3]
    task_name = "_".join(base_name)
    unittest_file = os.path.join(error_tasks_directory, f"{task_name}_unittest.py")

    for iteration in range(3):
        print(f"Iteration {iteration + 1} für Datei: {file_path}")
        if iteration == 0:
            corrected_code = analyze_error_with_openai(error_content)
        else:
            corrected_code = analyze_error_with_openai(error_content, unittest_output)

        if corrected_code:
            save_to_file(corrected_file_path, corrected_code)
            module_name = os.path.splitext(os.path.basename(corrected_file_path))[0]
            inject_module_import(unittest_file, module_name)
            success, unittest_output = run_unittest(unittest_file, module_name, corrected_file_path)
            print("Unittest-Ausgabe:")
            print(unittest_output)

            # Update iteration stats
            iteration_stats[iteration + 1]["total"] += 1
            if success:
                iteration_stats[iteration + 1]["success"] += 1
                return file_path, True, "Unittest erfolgreich"
            else:
                iteration_stats[iteration + 1]["failure"] += 1
        else:
            iteration_stats[iteration + 1]["total"] += 1
            iteration_stats[iteration + 1]["failure"] += 1
            return file_path, False, "Keine korrigierte Version erhalten"

    return file_path, False, "Keine Lösung nach drei Iterationen"


def main():
    error_files = get_error_files(error_tasks_directory)
    if not error_files:
        print("Keine Fehlerdateien gefunden.")
        return

    total_tests, successful_tests, failed_tests = 0, 0, 0

    # Initialize stats for each iteration
    iteration_stats = {1: {"total": 0, "success": 0, "failure": 0},
                       2: {"total": 0, "success": 0, "failure": 0},
                       3: {"total": 0, "success": 0, "failure": 0}}

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(process_file, file, iteration_stats): file for file in error_files}
        for future in as_completed(futures):
            file_path, success, message = future.result()
            total_tests += 1
            if success:
                successful_tests += 1
            else:
                failed_tests += 1
            print(f"Ergebnis für {file_path}: {message}")

    # Print overall stats
    print(f"\nGesamtzahl der Tests: {total_tests}")
    print(f"Erfolgreiche Tests: {successful_tests}")
    print(f"Fehlgeschlagene Tests: {failed_tests}")
    if total_tests > 0:
        print(f"Erfolgsquote: {(successful_tests / total_tests) * 100:.2f}%")

    # Print iteration stats
    for iteration, stats in iteration_stats.items():
        print(f"\nIteration {iteration}:")
        print(f"  Tests insgesamt: {stats['total']}")
        print(f"  Erfolgreiche Tests: {stats['success']}")
        print(f"  Fehlgeschlagene Tests: {stats['failure']}")
        if stats["total"] > 0:
            success_rate = (stats["success"] / stats["total"]) * 100
            print(f"  Erfolgsquote: {success_rate:.2f}%")
        else:
            print("  Keine Tests durchgeführt.")


if __name__ == "__main__":
    main()

