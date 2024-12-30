from fastapi import FastAPI

from delete_data import router as delete_router
from export_data import router as export_router
from insert_single_data import router as single_data_router
from upload_data import create_table
from upload_data import router as csv_upload_router
from view_data import router as view_data_router

# Initialize FastAPI app
app = FastAPI()

# Include the routers
app.include_router(csv_upload_router)
app.include_router(single_data_router)
app.include_router(view_data_router)
app.include_router(delete_router)
app.include_router(export_router)


# Create the table on app startup
@app.on_event("startup")
def startup():
    create_table()
