import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

COLUMNS = ['A', 'B', 'C']

def task_func(a, b):
    if not a or not b: 
        fig, ax = plt.subplots()  
        plt.close(fig)  
        return ax

    np.random.seed(0)
    selected_columns = COLUMNS[:len(a)] # Fehler: Hier sollte len(b) stehen
    df = pd.DataFrame(np.random.randn(len(a), len(b)), index=a, columns=selected_columns)
    ax = df.plot(kind='bar')
    plt.show()
    return ax

# Position des Fehlers: Zeile 14
# Subkategorie des Fehlers: Falsche Variable in einer Berechnung