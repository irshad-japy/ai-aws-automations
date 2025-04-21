"""
python3 -m scripts.sample_polars
"""

import polars as pl

# Sample data as a dictionary
data = {
    'Name': ['Alice', 'Bob', 'Charlie', 'David'],
    'Age': [25, 30, 35, 40],
    'City': ['New York', 'Los Angeles', 'Chicago', 'Houston']
}

# Create Polars DataFrame
df = pl.DataFrame(data)

# Display DataFrame
print(df)
