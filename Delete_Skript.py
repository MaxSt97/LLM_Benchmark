import os

# Verzeichnis, in dem die Dateien gelöscht werden sollen
error_tasks_directory = "tasks/error_tasks"

def delete_temp_files(directory):
    """Löscht alle Dateien in einem Verzeichnis, die auf '_temp.py' enden."""
    try:
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path) and file.endswith("_temp.py"):
                os.remove(file_path)
                print(f"Gelöscht: {file_path}")
        print("Alle '_temp.py'-Dateien wurden gelöscht.")
    except Exception as e:
        print(f"Fehler beim Löschen der Dateien: {e}")

# Funktion aufrufen
delete_temp_files(error_tasks_directory)
