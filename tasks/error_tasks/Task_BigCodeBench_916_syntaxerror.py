import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def task_func(df):
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    boxplot_ax = sns.boxplot(x=df['closing_price'], ax=axes[0])
    boxplot_ax.set_title('Box Plot of Closing Prices')
    
    histplot_ax = sns.histplot(df['closing_price'], kde=True, ax=axes[1])
    histplot_ax.set_title('Histogram of Closing Prices')
    
    plt.tight_layout()
    plt.close(fig)

        return boxplot_ax, histplot_ax
