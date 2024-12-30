import io

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile

from common_db import get_db_connection

# Initialize FastAPI router
router = APIRouter()


# Create or replace the database table with 'id' as the primary key
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Drop and create the table
    cursor.execute("DROP TABLE IF EXISTS heart_disease_data;")
    create_table_query = """
    CREATE TABLE  IF NOT EXISTS heart_disease_data (
        id INTEGER PRIMARY KEY,
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
    cursor.execute(create_table_query)
    conn.commit()
    conn.close()


# Perform validation on the dataframe
def validate_data(df: pd.DataFrame):
    errors = []

    if (df["age"] < 0).any():
        errors.append("Warning: Age cannot be negative.")
    if (df["trestbps"] <= 0).any():
        errors.append("Warning: Resting blood pressure (trestbps) should be positive.")
    if (df["chol"] <= 0).any():
        errors.append("Warning: Cholesterol level (chol) should be positive.")
    if (df["thalach"] <= 0).any():
        errors.append("Warning: Maximum heart rate (thalach) should be positive.")
    if (df["oldpeak"] < 0).any():
        errors.append(
            "Warning: Oldpeak (depression of ST segment) should not be negative."
        )
    if (df["ca"] < 0).any() or (df["ca"] > 3).any():
        errors.append("Warning: CA should be between 0 and 3.")
    if (df["slope"] < 1).any() or (df["slope"] > 3).any():
        errors.append("Warning: Slope should be between 1 and 3.")
    invalid_thal = df[~df["thal"].isin([3, 6, 7])]
    if not invalid_thal.empty:
        errors.append("Warning: Thal should be either 3, 6, or 7. Invalid rows:")

    return errors


# Insert data into the SQLite table
def insert_data(df: pd.DataFrame):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Add 'id' column from index (row number)
    df["id"] = df.index

    # Filter valid data based on validation
    valid_data = df[
        (df["age"] >= 0)
        & (df["trestbps"] > 0)
        & (df["chol"] > 0)
        & (df["thalach"] > 0)
        & (df["oldpeak"] >= 0)
        & (df["ca"] >= 0)
        & (df["ca"] <= 3)
        & (df["slope"] >= 1)
        & (df["slope"] <= 3)
        & df["thal"].isin([3, 6, 7])
    ]

    # Convert the dataframe to a list of tuples for insertion, including the 'id' column
    records = valid_data[
        [
            "id",
            "age",
            "sex",
            "cp",
            "trestbps",
            "chol",
            "fbs",
            "restecg",
            "thalach",
            "exang",
            "oldpeak",
            "slope",
            "ca",
            "thal",
        ]
    ].values.tolist()

    cursor.executemany(
        """
    INSERT INTO heart_disease_data (id, age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """,
        records,
    )
    conn.commit()
    conn.close()


# Function to validate if the file is CSV based on its content type
def is_csv(file: UploadFile):
    # Check if the file's content type is text/csv or application/csv
    if file.content_type not in ["text/csv", "application/csv"]:
        raise HTTPException(
            status_code=400, detail="Invalid file type. Only CSV files are allowed."
        )
    return True


@router.post("/upload_csv/")
async def upload_csv(file: UploadFile = File(...)):
    is_csv(file)
    try:
        # Read the file into a pandas DataFrame
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))

        # Perform validation and capture warnings
        validation_warnings = validate_data(df)

        # Log the warnings if any
        if validation_warnings:
            print(
                "\n".join(validation_warnings)
            )  # This prints warnings to the console for visibility.

        # Insert data into SQLite database (even if there are warnings)
        insert_data(df)

        return {
            "message": "Data inserted successfully.",
            "total_rows": len(df),
            "valid_rows": len(
                df[
                    (df["age"] >= 0)
                    & (df["trestbps"] > 0)
                    & (df["chol"] > 0)
                    & (df["thalach"] > 0)
                    & (df["oldpeak"] >= 0)
                    & (df["ca"] >= 0)
                    & (df["ca"] <= 3)
                    & (df["slope"] >= 1)
                    & (df["slope"] <= 3)
                    & df["thal"].isin([3, 6, 7])
                ]
            ),
            "warnings": validation_warnings,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
