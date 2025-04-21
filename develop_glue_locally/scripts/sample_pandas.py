"""
python3 -m scripts.sample_pandas
"""

import pandas as pd

# Sample data as a dictionary
data = {
    'Name': ['Alice', 'Bob', 'Charlie', 'David'],
    'Age': [25, 30, 35, 40],
    'City': ['New York', 'Los Angeles', 'Chicago', 'Houston']
}

# Create DataFrame
df = pd.DataFrame(data)

# Display DataFrame
print(df)
