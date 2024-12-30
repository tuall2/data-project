from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ValidationError

from common_db import get_db_connection

# Initialize FastAPI router
router = APIRouter()


class HeartDiseaseData(BaseModel):
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


# Insert single data into SQLite table
def insert_single_data(data: HeartDiseaseData):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert the data into the database
    cursor.execute(
        """
    INSERT INTO heart_disease_data (age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """,
        (
            data.age,
            data.sex,
            data.cp,
            data.trestbps,
            data.chol,
            data.fbs,
            data.restecg,
            data.thalach,
            data.exang,
            data.oldpeak,
            data.slope,
            data.ca,
            data.thal,
        ),
    )
    conn.commit()
    inserted_id = cursor.lastrowid
    conn.close()
    return inserted_id


# Validate data
def validate_single_data(data: HeartDiseaseData):
    warnings = []

    # Perform validation similar to the previous approach
    if data.age < 0:
        warnings.append("Warning: Age cannot be negative.")
    if data.trestbps <= 0:
        warnings.append(
            "Warning: Resting blood pressure (trestbps) should be positive."
        )
    if data.chol <= 0:
        warnings.append("Warning: Cholesterol level (chol) should be positive.")
    if data.thalach <= 0:
        warnings.append("Warning: Maximum heart rate (thalach) should be positive.")
    if data.oldpeak < 0:
        warnings.append(
            "Warning: Oldpeak (depression of ST segment) should not be negative."
        )
    if data.ca is not None and (data.ca < 0 or data.ca > 3):
        warnings.append("Warning: CA should be between 0 and 3.")
    if data.slope < 1 or data.slope > 3:
        warnings.append("Warning: Slope should be between 1 and 3.")
    if data.thal not in [3, 6, 7]:
        warnings.append("Warning: Thal should be either 3, 6, or 7.")

    return warnings


# Endpoint to insert a single row of data
@router.post("/add_single_data/")
async def add_single_data(data: HeartDiseaseData):
    try:
        # Validate the data
        validation_warnings = validate_single_data(data)

        # Log the warnings (this is optional, you can return them in the response too)
        if validation_warnings:
            return {
                "message": "Data insertion error.",
                "id": None,
                "warnings": validation_warnings,
            }

        # Insert data into SQLite database
        inserted_id = insert_single_data(data)

        return {
            "message": "Data inserted successfully.",
            "id": inserted_id,
            "warnings": validation_warnings,
        }

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
