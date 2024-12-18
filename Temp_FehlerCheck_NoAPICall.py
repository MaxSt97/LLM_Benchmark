import unittest
import re
import os
import sys
import importlib

def run_tests_for_error_tasks(error_tasks_dir):
    """
    Führt dynamisch Unittests für fehlerhafte Dateien im angegebenen Verzeichnis aus.
    Bricht den Unittest ab, wenn der Import der Task fehlschlägt.

    Args:
        error_tasks_dir: Das Verzeichnis, das die fehlerhaften Dateien und Unittests enthält.
    """
    print(f"error_tasks_dir: {error_tasks_dir}")
    print(f"sys.path: {sys.path}")

    successful_tests = []

    for filename in os.listdir(error_tasks_dir):
        if filename.endswith("_unittest.py"):
            match = re.match(r"Task_BigCodeBench_(\d+)_unittest\.py", filename)
            if match:
                task_id = match.group(1)
                error_task_files = [
                    f"Task_BigCodeBench_{task_id}_logicerror.py",
                    f"Task_BigCodeBench_{task_id}_syntaxerror.py",
                    f"Task_BigCodeBench_{task_id}_runtimeerror.py",
                ]

                for error_task_file in error_task_files:
                    full_error_task_path = os.path.join(error_tasks_dir, error_task_file)
                    if os.path.exists(full_error_task_path):
                        try:
                            # Dynamischer Import mit importlib – Abbruch bei Fehler
                            module_name = "tasks.error_tasks." + error_task_file[:-3]
                            try:
                                imported_module = importlib.import_module(module_name)
                                print(f"Erfolgreich importiert: {module_name}")
                                globals().update(imported_module.__dict__)
                            except Exception as import_error:
                                print(f"Fehler beim Importieren von {error_task_file}: {import_error}")
                                break  # Beendet die innere Schleife bei Importfehler

                            with open(os.path.join(error_tasks_dir, filename), "r") as f:
                                unittest_code = f.read()

                            # Entferne alte Imports, die mit "from Task ..." beginnen
                            cleaned_unittest_code = re.sub(r"^from Task.*\n", "", unittest_code, flags=re.MULTILINE)

                            final_unittest_code = cleaned_unittest_code

                            # Führe den Unittest aus
                            exec(final_unittest_code, globals())

                            suite = unittest.TestLoader().loadTestsFromTestCase(TestCases)  # Ersetzen Sie 'TestTask' durch Ihren Klassennamen!
                            runner = unittest.TextTestRunner()
                            result = runner.run(suite)

                            if result.wasSuccessful():
                                successful_tests.append(error_task_file)

                        except Exception as e:
                            print(f"Fehler beim Ausführen des Unittests für {error_task_file}: {e}")

    print("\nErfolgreiche Unittests:")
    for filename in successful_tests:
        print(filename)


if __name__ == "__main__":
    error_tasks_dir = os.path.join("tasks", "error_tasks")
    error_tasks_dir = os.path.abspath(error_tasks_dir)
    sys.path.insert(0, os.path.dirname(error_tasks_dir))  # 'tasks' zu sys.path hinzufügen
    run_tests_for_error_tasks(error_tasks_dir)