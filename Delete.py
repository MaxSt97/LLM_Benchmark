import importlib
import subprocess
import sys
from pathlib import Path

def run_unittest(unittest_file, module_name, module_path):
    """Führt den Unittest aus und gibt das Ergebnis zurück."""
    try:
        # Dynamischer Import des korrigierten Moduls
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Unittest ausführen mit explizitem Python-Interpreter
        result = subprocess.run([sys.executable, unittest_file], capture_output=True, text=True)
        print("Unittest Output:")
        print(result.stdout)
        print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Fehler beim Ausführen des Unittests: {e}")
        return False

# Debugging-Informationen ausgeben
print("Python Executable:", sys.executable)
print("Python Path:", sys.path)

# Prüfen, ob geopandas verfügbar ist
try:
    import geopandas
    print("Geopandas verfügbar:", geopandas.__file__)
except ImportError as e:
    print("Fehler beim Importieren von geopandas:", e)

# Absolute Pfade für Dateien innerhalb des Containers
base_path = Path("/app/tasks/error_tasks")
unittest_file = str(base_path / "Task_BigCodeBench_187_unittest.py")
module_name = "Task_BigCodeBench_187_Laufzeitfehler_corrected"
module_path = str(base_path / "Task_BigCodeBench_187_Laufzeitfehler_corrected.py")
print(f"Importing module from: {module_path}")


# Unittest ausführen
run_unittest(unittest_file, module_name, module_path)
