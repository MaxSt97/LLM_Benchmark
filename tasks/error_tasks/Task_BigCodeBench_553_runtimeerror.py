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
    selected_columns = COLUMNS[:len(b)]
    df = pd.DataFrame(np.random.randn(len(a), len(b)), index=a, columns=selected_columns)

    df = df.plot(kind='bar')

    df['Extra'] = 1

    plt.show()
    return df


