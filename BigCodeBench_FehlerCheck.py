import os
import re
import subprocess
import importlib.util
from openai import OpenAI
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import csv
import threading
from collections import defaultdict


# API Key aus .env-Datei laden und OpenAI-Client initialisieren
load_dotenv()
api_key = os.getenv("secret_api_key_openrouter")
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)


# Verzeichnis mit den Fehlerdateien und Modelle, die getestet werden sollen
error_tasks_directory = "tasks/error_tasks"
models_to_test = ["google/gemini-pro-1.5","openai/gpt-4o-2024-11-20", "anthropic/claude-3.5-sonnet", "google/gemini-flash-1.5","openai/gpt-4o-mini-2024-07-18","anthropic/claude-3.5-haiku-20241022", "qwen/qwen-2.5-coder-32b-instruct","deepseek/deepseek-chat"]


# Lock für jede Unittest-Datei
unittest_locks = defaultdict(threading.Lock)


# Tracker für die Ergebnisse der einzelnen Modelle und Dateien
results_tracker = {}


# Hilfsfunktion zum Lesen aller Dateien im Ordner, die nicht auf 'unittest.py' enden
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


# Hilfsfunktion zum Lesen des Dateiinhalts
def read_file_content(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        print(f"Fehler beim Lesen der Datei {file_path}: {e}")
        return None


# Hilfsfunktion zur Fehleranalyse mit API
def analyze_error_with_openai(error_text, model_name, unittest_output=None):

    try:
        prompt = (
            f"Hier ist ein fehlerhafter Python-Code:\n\n{error_text}\n\n"
            "Korrigiere die Fehler und gib den vollständigen Code als Python-Markdown-Codeblock aus."
        )
        if unittest_output:
            prompt += (
                f"\n\nHier ist die Fehlermeldung des zuletzt ausgeführten Unittests:\n\n{unittest_output}\n\n"
                "Berücksichtige diese Fehlermeldung bei der Korrektur."
            )

        response = client.chat.completions.create(
            model=model_name,
            temperature=0.5,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        response_content = response.choices[0].message.content
        code_blocks = extract_code_blocks(response_content)
        return code_blocks[0] if code_blocks else response_content
    except Exception as e:
        import traceback
        # Grundlegende Fehlermeldung
        print(f"Fehler bei der Kommunikation mit der OpenAI API: {e}")
        # Detaillierte Fehlerspur ausgeben
        traceback.print_exc()
        # Falls die API-Antwort ein spezifisches Attribut enthält
        if hasattr(e, 'response') and e.response is not None:
            print("Detaillierte API-Antwort:")
            print(e.response)
        return f"Fehler bei der API-Anfrage: {e}"


# Hilfsfunktionen für Code-Extraktion
def extract_code_blocks(content):

    code_blocks = re.findall(r"```python(.*?)```", content, re.DOTALL)
    return [block.strip() for block in code_blocks]


# Hilfsfunktion zum Speichern von Dateien
def save_to_file(filename, content):

    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(content)
        time.sleep(1)  # Warte kurz, um sicherzustellen, dass die Datei gespeichert ist
    except Exception as e:
        print(f"Fehler beim Speichern der Datei {filename}: {e}")


# Hilfsfunktionen für Unittest-Import
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


# Hilfsfunktionen für Unittest-Ausführung
def run_unittest(unittest_file, module_name, module_path):

    try:
        time.sleep(1)  # Sicherstellen, dass Datei korrekt vorliegt

        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        unittest_dir = os.path.dirname(unittest_file)
        result = subprocess.run(
            ["python", os.path.basename(unittest_file)],
            capture_output=True,
            text=True,
            cwd=unittest_dir
        )

        output = result.stdout + result.stderr
        success = (result.returncode == 0)
        return success, output
    except Exception as e:
        print(f"Fehler beim Ausführen des Unittests: {e}")
        return False, str(e)


# Hilfsfunktion zum Verarbeiten einer Datei
def process_file(file_path, iteration_stats, model_name):
    if (model_name, file_path) not in results_tracker:
        results_tracker[(model_name, file_path)] = {
            "iterations": [None, None, None],
            "final_success": None
        }

    error_content = read_file_content(file_path)
    if not error_content:
        # Direkt als Fehlschlag markieren
        results_tracker[(model_name, file_path)]["iterations"][0] = False
        results_tracker[(model_name, file_path)]["final_success"] = False
        return file_path, False, "Keine Inhalte"

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

            # Wartezeit und Prüfung, ob Datei existiert
            max_wait_time = 10  # Maximal 10 Sekunden warten
            wait_interval = 0.5  # Alle 0.5 Sekunden prüfen
            waited_time = 0
            while not os.path.exists(corrected_file_path) and waited_time < max_wait_time:
                time.sleep(wait_interval)
                waited_time += wait_interval

            if not os.path.exists(corrected_file_path):
                iteration_stats[iteration + 1]["total"] += 1
                iteration_stats[iteration + 1]["failure"] += 1
                results_tracker[(model_name, file_path)]["iterations"][iteration] = False
                return file_path, False, "Korrigierte Datei wurde nicht gefunden"

            # Lock, damit nur ein Thread dieselbe Unittest-Datei nutzt
            with unittest_locks[unittest_file]:
                inject_module_import(unittest_file, module_name)
                success, unittest_output = run_unittest(unittest_file, module_name, corrected_file_path)

            print("Unittest-Ausgabe:")
            print(unittest_output)

            # Update iteration stats
            iteration_stats[iteration + 1]["total"] += 1

            if success:
                iteration_stats[iteration + 1]["success"] += 1

                # Hier direkt im results_tracker vermerken
                results_tracker[(model_name, file_path)]["iterations"][iteration] = True
                results_tracker[(model_name, file_path)]["final_success"] = True

                return file_path, True, "Unittest erfolgreich"
            else:
                iteration_stats[iteration + 1]["failure"] += 1
                results_tracker[(model_name, file_path)]["iterations"][iteration] = False
        else:  # Keine korrigierte Version oder kein Codeblock gefunden
            # Speichere die unveränderte API-Ausgabe in einer separaten Datei
            unmodified_output_path = file_path.replace(
                ".py", f"_unmodified_iteration{iteration + 1}.txt")
            save_to_file(unmodified_output_path, corrected_code)  # Speichern

            iteration_stats[iteration + 1]["total"] += 1
            iteration_stats[iteration + 1]["failure"] += 1
            results_tracker[(model_name, file_path)]["iterations"][iteration] = False
            return file_path, False, "Keine korrigierte Version erhalten"

    # Nach 3 Iterationen kein Erfolg
    results_tracker[(model_name, file_path)]["final_success"] = False
    return file_path, False, "Keine Lösung nach drei Iterationen"


# Hilfsfunktion zum Erstellen einer CSV-Datei aus den Ergebnissen
def create_csv_from_results(
    model_name,
    iteration_stats,
    total_tests,
    successful_tests,
    failed_tests
):
    csv_filename = f"log_{model_name.replace('/', '_')}.csv"
    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")

        # Kopfzeile für einzelne Tasks pro Iteration
        writer.writerow(["Task", "Iteration 1", "Iteration 2", "Iteration 3"])

        # Iteriere nur über (model_name, file_path) in results_tracker,
        # die auch zu unserem aktuellen Modell gehören
        for (m_name, f_path), data in results_tracker.items():
            if m_name != model_name:
                continue  # Nur das aktuelle Modell

            # Task-Name aus Pfad extrahieren
            task_name = re.sub(r'^tasks/error_tasks/', '', f_path)
            task_name = re.sub(r'\.py$', '', task_name)

            iteration_vals = []
            for val in data["iterations"]:
                if val is True:
                    iteration_vals.append("true")
                elif val is False:
                    iteration_vals.append("false")
                else:
                    # Falls None, hat die Iteration gar nicht stattgefunden
                    iteration_vals.append("false")  # oder "none", wie man mag

            row = [task_name] + iteration_vals
            writer.writerow(row)

        # Leerzeile
        writer.writerow([])
        # Gesamte Übersicht
        writer.writerow(["Globale Statistik"])
        writer.writerow(["Gesamtanzahl Tests", total_tests])
        writer.writerow(["Erfolgreiche Tests", successful_tests])
        writer.writerow(["Fehlgeschlagene Tests", failed_tests])
        if total_tests > 0:
            global_success_rate = (successful_tests / total_tests) * 100
            writer.writerow(["Erfolgsquote", f"{global_success_rate:.2f}%"])
        else:
            writer.writerow(["Erfolgsquote", "0.00%"])

        # Leerzeile
        writer.writerow([])
        # Iterationsübersicht
        writer.writerow(["Iterations-Statistik"])
        writer.writerow(["Iteration", "Tests insgesamt", "Erfolgreiche Tests", "Fehlgeschlagene Tests", "Erfolgsquote"])

        for iteration, stats in iteration_stats.items():
            iteration_total = stats["total"]
            iteration_success = stats["success"]
            iteration_failure = stats["failure"]

            if iteration_total > 0:
                iteration_success_rate = (iteration_success / iteration_total) * 100
                writer.writerow([
                    iteration,
                    iteration_total,
                    iteration_success,
                    iteration_failure,
                    f"{iteration_success_rate:.2f}%"
                ])
            else:
                writer.writerow([iteration, 0, 0, 0, "Keine Tests durchgeführt."])


# Hauptfunktion zum Starten der Tests
def main():
    error_files = get_error_files(error_tasks_directory)
    if not error_files:
        print("Keine Fehlerdateien gefunden.")
        return

    for model_name in models_to_test:
        print(f"\n\n--- Starte Tests mit Modell: {model_name} ---\n")
        total_tests = 0
        successful_tests = 0
        failed_tests = 0

        # Initialisiere die Statistiken pro Iteration (1, 2, 3)
        iteration_stats = {
            1: {"total": 0, "success": 0, "failure": 0},
            2: {"total": 0, "success": 0, "failure": 0},
            3: {"total": 0, "success": 0, "failure": 0},
        }

        # ThreadPoolExecutor zum parallelen Abarbeiten der Dateien
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {
                executor.submit(process_file, file, iteration_stats, model_name): file
                for file in error_files
            }
            for future in as_completed(futures):
                file_path, success, message = future.result()
                total_tests += 1
                if success:
                    successful_tests += 1
                else:
                    failed_tests += 1
                print(f"Ergebnis für {file_path} ({model_name}): {message}")

        # Ausgabe der Gesamtergebnisse auf der Konsole
        print(f"\nGesamtzahl der Tests ({model_name}): {total_tests}")
        print(f"Erfolgreiche Tests ({model_name}): {successful_tests}")
        print(f"Fehlgeschlagene Tests ({model_name}): {failed_tests}")
        if total_tests > 0:
            print(f"Erfolgsquote ({model_name}): {(successful_tests / total_tests) * 100:.2f}%")

        # Iterationsstatistiken (1..3)
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

        # CSV-Erzeugung auf Basis unserer gesammelten Daten
        create_csv_from_results(
            model_name,
            iteration_stats,
            total_tests,
            successful_tests,
            failed_tests
        )
        print(f"\n--- CSV 'log_{model_name}.csv' wurde erfolgreich erzeugt. ---")


if __name__ == "__main__":
    main()
