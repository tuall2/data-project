from typing import Optional

import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from common_db import get_db_connection

# Initialize FastAPI router
router = APIRouter()


# Function to fetch data from the SQLite database with pagination
def fetch_data(offset: int, limit: int):
    conn = get_db_connection()
    query = (
        f"SELECT * FROM heart_disease_data ORDER BY id LIMIT {limit} OFFSET {offset};"
    )
    df = pd.read_sql(query, conn)
    conn.close()
    return df


# View data endpoint with pagination support
@router.get("/view_data/")
async def view_data(offset: int = Query(0, ge=0), limit: int = Query(10, le=100)):
    """
    View data with pagination support.
    - `offset`: The number of rows to skip.
    - `limit`: The maximum number of rows to return (default: 10, max: 100).
    """
    try:
        # Fetch the data from the database with the given offset and limit
        df = fetch_data(offset, limit)

        # Convert the DataFrame to a dictionary to return it in the response
        data = df.to_dict(orient="records")

        # Return the data in the response
        return {
            "message": "Data retrieved successfully.",
            "data": data,
            "offset": offset,
            "limit": limit,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# Define a Pydantic model for the response format
class HeartDiseaseDataResponse(BaseModel):
    id: int
    age: int
    sex: int
    cp: int
    trestbps: int
    chol: int
    fbs: int
    restecg: int
    thalach: int
    exang: int
    oldpeak: float
    slope: int
    ca: Optional[float] = None
    thal: float


# Function to get data by ID from the database
def get_data_by_id(data_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query the database for the record with the given ID
    cursor.execute("SELECT * FROM heart_disease_data WHERE id = ?", (data_id,))
    row = cursor.fetchone()

    conn.close()

    return row


# Endpoint to get data by ID
@router.get("/view_id_data/{data_id}", response_model=HeartDiseaseDataResponse)
async def view_id_data(data_id: int):
    """
    View a single record by ID.
    - `data_id`: The ID of the record to retrieve.
    """
    row = get_data_by_id(data_id)

    if row is None:
        raise HTTPException(
            status_code=404, detail="Data not found with the provided ID."
        )

    # Create the response model from the row data
    response_data = HeartDiseaseDataResponse(
        id=row[0],
        age=row[1],
        sex=row[2],
        cp=row[3],
        trestbps=row[4],
        chol=row[5],
        fbs=row[6],
        restecg=row[7],
        thalach=row[8],
        exang=row[9],
        oldpeak=row[10],
        slope=row[11],
        ca=row[12],
        thal=row[13],
    )

    return response_data
