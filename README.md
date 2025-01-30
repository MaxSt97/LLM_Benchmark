# LLM_Benchmark

**Hintergrund**
Das vorliegende Skript dient der Automatisierung der Testdurchführung im Rahmen des LLM-Benchmarks mittels der OpenRouter-API. Die anderen vorhandenen Skripte dienen der Fehlererzeugung oder dienen als Arbeitserleichterung. 

1.  **Laden fehlerhafter Code-Dateien:** Liest Python-Dateien aus dem Verzeichnis `tasks/error_tasks`. Diese Dateien enthalten vermutlich absichtlich eingefügte Fehler (Syntaxfehler, Laufzeitfehler oder Logikfehler).
2.  **Iterative Fehlerbehebung:**
    *   Sendet den fehlerhaften Code an eines der ausgewählten LLMs (siehe `models_to_test`).
    *   Fordert das LLM auf, den Code zu korrigieren.
    *   Speichert den korrigierten Code in einer neuen Datei (`_corrected.py`).
    *   Führt Unittests (`_unittest.py`) gegen den korrigierten Code aus.
    *   Wenn die Unittests erfolgreich sind, wird der Task als erfolgreich markiert.
    *   Wenn die Unittests fehlschlagen, wird der Prozess bis zu drei Mal wiederholt, wobei die Fehlermeldung des Unittests dem LLM im nächsten Versuch mitgegeben wird.
3.  **Ergebnisprotokollierung:**
    *   Gibt die Ergebnisse jedes Modells und jeder Datei in der Konsole aus.
    *   Erstellt für jedes getestete Modell eine CSV-Datei (`log_<Modellname>.csv`), die detaillierte Ergebnisse für jede Iteration.

**Modelle:**

Das Skript unterstützt die folgenden LLMs über die OpenRouter-API:

*   `google/gemini-pro-1.5`
*   `openai/gpt-4o-2024-11-20`
*   `anthropic/claude-3.5-sonnet-20241022`
*   `google/gemini-flash-1.5`
*   `openai/gpt-4o-mini-2024-07-18`
*   `anthropic/claude-3.5-haiku-20241022`
*   `qwen/qwen-2.5-coder-32b-instruct`
*   `deepseek/deepseek-chat`

**Voraussetzungen:**

*   **Docker:** Das Skript ist für die Ausführung in einem Docker-Container konzipiert.
*   **Python 3.10:** Das Basis-Image ist `python:3.10-slim`.
*   **.env-Datei:** Eine `.env`-Datei im Hauptverzeichnis muss einen API-Schlüssel für OpenRouter enthalten:
    ```
    secret_api_key_openrouter=<Ihr OpenRouter API-Schlüssel>
    ```
*   **requirements.txt:** Diese Datei enthät alle benötigten Python-Pakete.

**Ausführung:**

1.  Erstellen Sie ein Docker-Image aus dem beigefügten Dockerfile:
    ```bash
    docker build -t bigcodebench-fehlercheck .
    ```
2.  Starten Sie einen Docker-Container:
    ```bash
    docker run -it bigcodebench-fehlercheck
    ```

**Ausgabe:**

*   **Konsolenausgabe:** Zeigt den Fortschritt und die Ergebnisse der Tests für jedes Modell und jede Datei an.
*   **CSV-Dateien:** Detaillierte Ergebnisse pro Modell in `log_<Modellname>.csv`. Diese Dateien enthalten:

**Hinweis:**

*   Der Code verwendet Threading für die parallele Verarbeitung von Dateien.
*   Unittests werden für jede korrigierte Datei ausgeführt, um die Korrektheit der Korrekturen zu überprüfen.
*   Die maximale Anzahl an Iterationen pro Datei ist auf 3 begrenzt.

**Anpassung:**

*   **`models_to_test`:**  Ändere diese Liste, um andere LLMs von OpenRouter zu testen.
*   **`error_tasks_directory`:** Passe dieses Verzeichnis an, wenn sich deine Fehler-Tasks an einem anderen Ort befinden.
*   **`max_workers` in `ThreadPoolExecutor`:** Passe die Anzahl der Threads für die Parallelverarbeitung an.






