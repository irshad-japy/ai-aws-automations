"""
set PYSPARK_PYTHON=python
set PYSPARK_DRIVER_PYTHON=python
python pyspark/pyspark_ai_poc.py
or
python -m pyspark.pyspark_ai_poc
"""

import os
from pyspark.sql import SparkSession
from pyspark_ai import SparkAI
from langchain.chat_models import ChatOpenAI

# Step 1: Set your OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Replace with your actual key

# Step 2: Create Spark Session
spark = SparkSession.builder \
    .appName("PySpark AI Demo") \
    .getOrCreate()

# Use 'gpt-3.5-turbo' (might lower output quality)
# Step 3: Initialize SparkAI
llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
spark_ai = SparkAI(llm=llm, verbose=True)
spark_ai.activate()

# Step 4: Sample DataFrame
data = [
    ("James", "Smith", "USA", "CA", 200000),
    ("Michael", "Rose", "USA", "NY", 150000),
    ("Robert", "Williams", "USA", "CA", 120000),
    ("Maria", "Jones", "USA", "NY", 130000),
    ("Ramana", "Madala", "India", "AP", 40000),
    ("Chandra", "Potte", "India", "AP", 50000),
    ("Krishna", "Murugan", "India", "TN", 40000),
    ("Saravanan", "Murugan", "India", "TN", 40000),
]
columns = ["firstname", "lastname", "country", "state", "salary"]

df = spark.createDataFrame(data, columns)

# Step 5: Perform transformations using English queries
print("\n👉 Query 1: Average salary by country")
df.ai.transform("Show the average salary by country").show()

print("\n👉 Query 2: Filter salaries > 100000")
df.ai.transform("Show all records where salary is greater than 100000").show()

print("\n👉 Query 3: Group by state and average salary")
df.ai.transform("Group the data by state and calculate the average salary").show()

# Step 6: Optional - Generate a plot (requires matplotlib)
try:
    print("\n👉 Generating bar chart of average salary by state...")
    df.ai.plot("Bar chart of average salary by state")
except Exception as e:
    print("⚠️ Plotting failed (optional step):", e)

# Step 7: Optional - Explain the DataFrame structure
print("\n👉 Explaining the DataFrame...")
print(df.ai.explain())

# Step 8: Optional - Condition verification
print("\n👉 Verifying salary condition...")
print(df.ai.verify("All salaries are above 30000"))

# Stop Spark session
spark.stop()
