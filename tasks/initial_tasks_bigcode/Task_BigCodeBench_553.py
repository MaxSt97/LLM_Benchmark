import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

COLUMNS = ['A', 'B', 'C']  # Beispielhafte Spaltennamen

def task_func(a, b):
    if not a or not b:  # Überprüfen, ob eine der Listen leer ist
        fig, ax = plt.subplots()  # Erstellt ein leeres Diagramm
        plt.close(fig)  # Schließt das Diagrammfenster, um leere Diagramme zu vermeiden
        return ax

    # Verwende np.random.seed für Reproduzierbarkeit, falls erforderlich
    np.random.seed(0)
    # Stelle sicher, dass die Spaltennamen von b nur bis zur Länge von b verwendet werden
    selected_columns = COLUMNS[:len(b)]
    df = pd.DataFrame(np.random.randn(len(a), len(b)), index=a, columns=selected_columns)
    ax = df.plot(kind='bar')
    plt.show()
    return ax