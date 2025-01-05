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
import csv

# Original-Print flushen:
print = functools.partial(print, flush=True)

# Wir puffern die Ausgaben in log_buffer.
log_buffer = []
old_print = print

def capturing_print(*args, **kwargs):
    text = " ".join(str(a) for a in args)
    log_buffer.append(text)
    return old_print(*args, **kwargs)

print = capturing_print


# Lade die API-Schlüssel aus der .env-Datei
load_dotenv()

# Erstelle eine OpenAI-Instanz
api_key = os.getenv("secret_api_key_openai")
client = OpenAI(api_key=api_key)

# Verzeichniss festlegen
error_tasks_directory = "tasks/error_tasks"

# Liste der zu testenden Modelle
models_to_test = ["gpt-4o-mini"]  

# Hilfsfunktionen zur Auflistung von Dateien, die nicht auf unittest.py enden
def get_error_files(directory):

    try:
        return [
            os.path.join(directory, file)
            for file in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, file)) and not file.endswith("unittest.py")
        ]
    except Exception as e:
        print(f"Fehler beim Lesen des Verzeichnisses: {e}")
        return []

# Hilfsfunktionen zur Dateiverarbeitung
def read_file_content(file_path):

    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        print(f"Fehler beim Lesen der Datei {file_path}: {e}")
        return None

# Hilfsfunktionen zur Fehleranalyse mittels LLM
def analyze_error_with_openai(error_text, model_name, unittest_output=None):

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
            model=model_name,
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

# Hilfsfunktionen zur Extraktion von Codeblöcken aus Markdown
def extract_code_blocks(content):

    code_blocks = re.findall(r"`python(.*?)`", content, re.DOTALL)
    return [block.strip() for block in code_blocks]

# Hilfsfunktion zur Speicherung des korrigierten Codes
def save_to_file(filename, content):

    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(content)
        time.sleep(1)  # Warte kurz, um sicherzustellen, dass die Datei gespeichert ist
    except Exception as e:
        print(f"Fehler beim Speichern der Datei {filename}: {e}")

# Hilfsfunktionen zum dynmaischen Import der jeweiligen Datei des Unittests
def inject_module_import(unittest_file_path, module_name):

    try:
        unittest_code = read_file_content(unittest_file_path)
        if unittest_code is None:
            return False

        # Entferne alte Importe, die mit 'from Task_' beginnen
        unittest_code = re.sub(r"^from Task_.*\n", "", unittest_code, flags=re.MULTILINE)

        # Füge den neuen Import hinzu
        import_statement = f"from {module_name} import *\n"
        if import_statement not in unittest_code:
            unittest_code = import_statement + unittest_code
            with open(unittest_file_path, "w", encoding="utf-8") as file:
                file.write(unittest_code)
        return True
    except Exception as e:
        print(f"Fehler beim Importieren des Moduls: {e}")
        return False

# Hilfsfunktionen zum Ausführen des Unittests
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

# Hilfsfunktionen zum Aufruf des LLM mit maximal drei Iterationen
def process_file(file_path, iteration_stats, model_name):

    error_content = read_file_content(file_path)
    if not error_content:
        return file_path, False, "Keine Inhalte"

    corrected_code = None
    corrected_file_path = file_path.replace(".py", "_corrected.py")
    base_name = os.path.basename(file_path).split("_")[0:3]
    task_name = "_".join(base_name)
    unittest_file = os.path.join(error_tasks_directory, f"{task_name}_unittest.py")

    unittest_output = None

    for iteration in range(3):
        print(f"Modell: {model_name}, Iteration {iteration + 1} für Datei: {file_path}")
        if iteration == 0:
            corrected_code = analyze_error_with_openai(error_content, model_name)
        else:
            corrected_code = analyze_error_with_openai(error_content, model_name, unittest_output)

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

# Hauptprozess
def main():
    error_files = get_error_files(error_tasks_directory)
    if not error_files:
        print("Keine Fehlerdateien gefunden.")
        return

    for model_name in models_to_test:
        print(f"\n\n--- Starte Tests mit Modell: {model_name} ---\n")
        total_tests, successful_tests, failed_tests = 0, 0, 0

        # Initialize stats for each iteration
        iteration_stats = {
            1: {"total": 0, "success": 0, "failure": 0},
            2: {"total": 0, "success": 0, "failure": 0},
            3: {"total": 0, "success": 0, "failure": 0},
        }

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(process_file, file, iteration_stats, model_name): file for file in error_files}
            for future in as_completed(futures):
                file_path, success, message = future.result()
                total_tests += 1
                if success:
                    successful_tests += 1
                else:
                    failed_tests += 1
                print(f"Ergebnis für {file_path} ({model_name}): {message}")

        # Ausgabe der Statistik übergeordnet
        print(f"\nGesamtzahl der Tests ({model_name}): {total_tests}")
        print(f"Erfolgreiche Tests ({model_name}): {successful_tests}")
        print(f"Fehlgeschlagene Tests ({model_name}): {failed_tests}")
        if total_tests > 0:
            print(f"Erfolgsquote ({model_name}): {(successful_tests / total_tests) * 100:.2f}%")

        # Ausgabe der Statistik für jede Iteration
        for iteration, stats in iteration_stats.items():
            print(f"\nIteration {iteration} ({model_name}):")
            print(f"  Tests insgesamt: {stats['total']}")
            print(f"  Erfolgreiche Tests: {stats['success']}")
            print(f"  Fehlgeschlagene Tests: {stats['failure']}")
            if stats["total"] > 0:
                success_rate = (stats["success"] / stats["total"]) * 100
                print(f"  Erfolgsquote: {success_rate:.2f}%")
            else:
                print("  Keine Tests durchgeführt.")

        # 2) Nach Ende jeder Modell-Iteration: CSV erzeugen & "fremde" Dateien ignorieren
        parse_and_create_csv(log_buffer, model_name)
        print(f"\n--- CSV 'log_{model_name}.csv' wurde erfolgreich erzeugt. ---")
        log_buffer.clear() # Leere den log_buffer für das nächste Modell

# Hilfsfunktion für die Logdatenanalyse und -export
def parse_and_create_csv(log_lines, model_name):

    pattern_iteration = re.compile(r"Modell:\s+(.*?), Iteration\s+(\d+)\s+für\s+Datei:\s+(.*)")
    pattern_result    = re.compile(r"Ergebnis\s+für\s+(.*?)\s+\((.*?)\):\s+(.*)")

    task_dict = {}
    current_iter = None
    current_model = None

    for line in log_lines:
        it_match = pattern_iteration.search(line)
        if it_match:
            current_model = it_match.group(1)
            current_iter = int(it_match.group(2))
            filepath     = it_match.group(3)

            if current_model != model_name:  # Nur Zeilen für das aktuelle Modell beachten
                continue

            task_name = re.sub(r'^tasks/error_tasks/', '', filepath)
            task_name = re.sub(r'\.py$', '', task_name)

            if task_name not in task_dict:
                task_dict[task_name] = [None, None, None]

        else:
            res_match = pattern_result.search(line)
            if res_match:
                file_in_result = res_match.group(1)
                model_in_result = res_match.group(2)
                msg            = res_match.group(3)

                if model_in_result != model_name:  # Nur Zeilen für das aktuelle Modell beachten
                    continue

                # Prüfen, ob wir es mit einer .py-Datei zu tun haben:
                if not file_in_result.endswith(".py"):
                    # -> z. B. 'scraped_data.csv' => ignorieren
                    continue

                # mapped task name
                file_in_result = re.sub(r'^tasks/error_tasks/', '', file_in_result)
                file_in_result = re.sub(r'\.py$', '', file_in_result)

                # Falls kein Dictionary-Eintrag vorhanden, ignorieren:
                if file_in_result not in task_dict:
                    continue

                # Erfolg?
                success = ("Unittest erfolgreich" in msg)
                if current_iter is not None:
                    idx = current_iter - 1
                    if success:
                        task_dict[file_in_result][idx] = True
                        # Falls es in dieser Iteration bereits erfolgreich war,
                        # markiere alle danach noch None als false
                        for i in range(current_iter, 3):
                            if task_dict[file_in_result][i] is None:
                                task_dict[file_in_result][i] = False
                    else:
                        task_dict[file_in_result][idx] = False

                    # Falls "Keine Lösung nach drei Iterationen" => alle false
                    if "Keine Lösung nach drei Iterationen" in msg:
                        for i in range(3):
                            if task_dict[file_in_result][i] is None:
                                task_dict[file_in_result][i] = False

    # CSV schreiben
    with open(f"log_{model_name}.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        writer.writerow(["Task", "Iteration 1", "Iteration 2", "Iteration 3"])

        for task_name, iteration_results in task_dict.items():
            # z. B. [True, False, None]
            # None => hat in der Iteration gar keine Info -> als false werten
            iteration_values = []
            for val in iteration_results:
                if val is None:
                    iteration_values.append("false")
                else:
                    iteration_values.append(str(val).lower())
            row = [task_name] + iteration_values
            writer.writerow(row)


if __name__ == "__main__":
    main()

