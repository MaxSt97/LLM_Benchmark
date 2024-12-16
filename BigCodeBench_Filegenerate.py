import os
import shutil

# Verzeichnisse festlegen
initial_tasks_dir = "tasks/initial_tasks_bigcode"
error_tasks_dir = "tasks/error_tasks"

os.makedirs(error_tasks_dir, exist_ok=True)

# Hauptprozess: Für alle Task-Dateien
task_files = [f for f in os.listdir(initial_tasks_dir) if f.endswith(".py") and not f.endswith("_unittest.py")]
for task_file in task_files:
    task_path = os.path.join(initial_tasks_dir, task_file)

    with open(task_path, "r", encoding="utf-8") as file:
        original_code = file.read()

    # Kopieren der Datei in drei Kategorien mit umbenannten Namen
    for error in ["Syntaxfehler", "Logikfehler", "Laufzeitfehler"]:
        new_file_name = f"{task_file.split('.')[0]}_{error}.py"
        error_code_path = os.path.join(error_tasks_dir, new_file_name)
        with open(error_code_path, "w", encoding="utf-8") as new_file:
            new_file.write(original_code)
        print(f"Datei {task_file} wurde als {new_file_name} kopiert.")

# Kopieren der Unittest-Dateien ins Fehlerverzeichnis
unittest_files = [f for f in os.listdir(initial_tasks_dir) if f.endswith("_unittest.py")]
for unittest_file in unittest_files:
    source_path = os.path.join(initial_tasks_dir, unittest_file)
    destination_path = os.path.join(error_tasks_dir, unittest_file)
    shutil.copy(source_path, destination_path)
    print(f"Unittest-Datei {unittest_file} wurde nach {error_tasks_dir} kopiert.")
