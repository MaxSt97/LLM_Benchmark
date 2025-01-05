# Basis-Image
FROM python:3.10-slim

# Installieren der Systemabhängigkeiten
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Arbeitsverzeichnis
WORKDIR /app

# Kopieren der requirements.txt
COPY requirements.txt /app/

# Installieren der Python-Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Kopieren des restlichen Codes
COPY . /app/

# Standardbefehl
CMD ["python", "Temp_Fehlercheck_I.py"]

