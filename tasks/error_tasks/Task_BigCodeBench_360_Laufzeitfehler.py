import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def task_func(file_location, sheet_name):
    if not os.path.exists(file_location):
        raise FileNotFoundError(f"No file found at {file_location}")

    try:
        df = pd.read_excel(file_location, sheet_name=sheet_name)
    except ValueError as e:
        raise ValueError(f"Error reading sheet: {e}")

    result = {}
    fig, ax = plt.subplots()
    for column in df.columns:
        mean = np.mean(df[column])
        std = np.std(df[column])
        std = std.mean()
        result[column] = {"mean": mean, "std": std}

        ax.bar(column, mean, yerr=std)

    ax.set_title('Mean and Standard Deviation')
    ax.set_xlabel('Columns')
    ax.set_ylabel('Values')

    return result, fig