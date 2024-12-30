import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect("database/heart_disease.db")
cursor = conn.cursor()

# Drop the table if it exists and then recreate it
# drop_table_query = "DROP TABLE IF EXISTS heart_disease_data;"
# cursor.execute(drop_table_query)

# Define the table creation query with an 'id' column as the primary key
create_table_query = """
CREATE TABLE database/heart_disease_data (
    id INTEGER PRIMARY KEY,  -- Unique identifier for each row
    age INTEGER,
    sex INTEGER,
    cp INTEGER,
    trestbps INTEGER,
    chol INTEGER,
    fbs INTEGER,
    restecg INTEGER,
    thalach INTEGER,
    exang INTEGER,
    oldpeak REAL,
    slope INTEGER,
    ca REAL,
    thal REAL
);
"""

# Execute the table creation query
cursor.execute(create_table_query)
conn.commit()

# Close the connection
conn.close()
