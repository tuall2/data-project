from fastapi import APIRouter, HTTPException

from common_db import get_db_connection

# Initialize FastAPI router
router = APIRouter()


# Function to delete data from the SQLite database by ID
def delete_data_by_id(data_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Attempt to delete the record
    cursor.execute("DELETE FROM heart_disease_data WHERE id = ?", (data_id,))

    # Commit the transaction
    conn.commit()

    # Check if any row was deleted
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(
            status_code=404, detail="Data not found with the provided ID."
        )

    conn.close()


# Delete data endpoint
@router.delete("/delete_data/{data_id}")
async def delete_data(data_id: int):
    """
    Delete a single record by ID.
    - `data_id`: The ID of the record to be deleted.
    """
    try:
        # Call the function to delete the data by ID
        delete_data_by_id(data_id)
        return {"message": f"Data with ID {data_id} deleted successfully."}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# Function to delete all data in the table
def delete_all_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Delete all records in the table
    cursor.execute("DELETE FROM heart_disease_data")
    conn.commit()
    conn.close()


# Endpoint to delete all data in the table
@router.delete("/delete_all_data/")
async def delete_all_data_endpoint():
    """
    Delete all records from the heart_disease_data table.
    """
    try:
        # Delete all data from the table
        delete_all_data()

        return {"message": "All data deleted successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
