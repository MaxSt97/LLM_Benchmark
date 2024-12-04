import os
from openai import OpenAI
from dotenv import load_dotenv
import re

# OpenAI API-Key initialisieren
load_dotenv()
api_key = os.getenv("secret_api_key_openai")
client = OpenAI(api_key=api_key)

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
            messages=[
                {"role": "user", "content": f"Bitte analysiere den folgenden fehlerhaften Code und korrigiere ihn: {error_text},"
                                            f"Gib den korrigierten Code als Python-Codeblock im Markdown-Format zurück."}
            ]
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

def main():
    error_files = get_error_files(error_tasks_directory)
    if not error_files:
        print("Keine Fehlerdateien gefunden.")
        return

    for file_path in error_files:
        print(f"Analysiere Datei: {file_path}")
        error_content = read_file_content(file_path)
        if error_content:
            print(f"Fehlerinhalt:\n{error_content}")
            analysis = analyze_error_with_openai(error_content)
            if analysis:
                print(f"Analyse von OpenAI:\n{analysis}\n")
            else:
                print("Keine Analyse erhalten.\n")
        else:
            print("Fehler konnte nicht gelesen werden.\n")

if __name__ == "__main__":
    main()
