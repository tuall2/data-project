import csv

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from common_db import get_db_connection

# Initialize FastAPI router
router = APIRouter()


# Function to fetch all data from the database
def get_all_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query all data from the table
    cursor.execute("SELECT * FROM heart_disease_data")
    rows = cursor.fetchall()

    conn.close()
    return rows


# Function to export data to a CSV file
def export_to_csv(data):
    # Define the file path for the CSV file
    csv_filename = "heart_disease_data_export.csv"

    # Open the CSV file in write mode
    with open(csv_filename, mode="w", newline="") as file:
        writer = csv.writer(file)

        # Write the header (column names)
        writer.writerow(
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
        )

        # Write all rows of data
        writer.writerows(data)

    return csv_filename


# Endpoint to export all data as a CSV file
@router.get("/export_data_as_csv/")
async def export_data_as_csv():
    """
    Export all data from the heart_disease_data table as a CSV file.
    """
    try:
        # Fetch all data from the database
        data = get_all_data()

        if not data:
            raise HTTPException(status_code=404, detail="No data available to export.")

        # Export the data to a CSV file
        csv_filename = export_to_csv(data)

        # Return the CSV file as a response
        return FileResponse(csv_filename, media_type="text/csv", filename=csv_filename)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
