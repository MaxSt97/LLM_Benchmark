import os

# Verzeichnis, in dem die Dateien gelöscht werden sollen
error_tasks_directory = "tasks/error_tasks"

# Hilfsfunktionen für das Löschen von Dateien
def delete_temp_files(directory):
    try:
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path) and file.endswith("_temp.py"):
                os.remove(file_path)
                print(f"Gelöscht: {file_path}")
        print("Alle '_temp.py'-Dateien wurden gelöscht.")
    except Exception as e:
        print(f"Fehler beim Löschen der Dateien: {e}")


# Löschen der temporären Dateien
delete_temp_files(error_tasks_directory)


# Hilfsfunltionen für das Löschen von Dateien
def delete_temp_filesI(directory):
    try:
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path) and file.endswith("_corrected.py"):
                os.remove(file_path)
                print(f"Gelöscht: {file_path}")
        print("Alle '_temp.py'-Dateien wurden gelöscht.")
    except Exception as e:
        print(f"Fehler beim Löschen der Dateien: {e}")


# Löschen der temporären Dateien
delete_temp_filesI(error_tasks_directory)