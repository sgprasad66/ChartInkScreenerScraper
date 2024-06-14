''' Sure, here is a Python code snippet that should do what you're asking for. This code assumes that your data is stored in CSV files and that these files are named in a way that allows sorting them in chronological order (e.g., "data_2024-04-10.csv", "data_2024-04-09.csv", etc.). 

```python '''


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
from collections import Counter

def process_data(directory, days):
    # Get list of files in directory
    files = sorted(os.listdir(directory))

    # Read the data from the last 'days' files into dataframes
    dataframes = [pd.read_csv(os.path.join(directory, file)) for file in files[-days:]]

    # Concatenate all dataframes
    df = pd.concat(dataframes)

    # Get counts for each day and for all days
    counts = [Counter(dataframe['nsecode']) for dataframe in dataframes]
    cumulative_counts = Counter(df['nsecode'])

    # Prepare the final dataframe
    final_df = pd.DataFrame.from_dict(cumulative_counts, orient='index', columns=['cumulative-count'])
    for i, count in enumerate(counts):
        final_df[f'count_{i+1}'] = final_df.index.map(count).fillna(0).astype(int)

    print(final_df)

    # Plot the data
    final_df.reset_index().melt('index').rename(columns={'index':'nsecode'}).pipe((sns.catplot,'data'), x='nsecode', y='value', hue='variable', kind='bar', height=5, aspect=2)
    plt.show()

# Example usage:
process_data('D:\FilesFromRoopesh\OptionsPakshiResampling\ChartInkScreenerScraper\csvfiles', 2)
'''
```

This code first reads the data from the specified number of most recent files into separate pandas dataframes. It then concatenates these dataframes into one. For each day and for all days combined, it counts the occurrences of each 'nsecode'. These counts are then combined into the final dataframe. Finally, it prints this dataframe and creates a bar plot of the data using seaborn.

Please replace `'/path/to/your/csv/files'` with the path to the directory containing your CSV files. The argument `3` specifies the number of days (i.e., files) to consider; you can replace this with any number you like. 

Please note that this code does not handle errors that might occur when reading the files. Depending on your exact requirements and the reliability of your data, you might want to add error handling code. Also, this code does not save the plot to a file, but you can easily do this by calling `plt.savefig('/path/to/plot.png')` after `plt.show()`. Replace `'/path/to/plot.png'` with the desired path and filename for the plot. 

Let me know if you need further assistance!'''