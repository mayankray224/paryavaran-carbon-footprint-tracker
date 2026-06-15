"""
Main entry point for the Paryavaran carbon footprint tracker application.
Starts the FastAPI application, initializes database schemas, and runs uvicorn.
"""
import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from src.models.database import init_db
from src.api.routes import router

# Initialize database tables
init_db()

# Create FastAPI instance
app = FastAPI(
    title="Paryavaran Carbon Footprint Tracker",
    description="Help individuals understand, track, and reduce their carbon footprint.",
    version="1.0.0"
)

# CORS middleware configuration for secure access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this in production settings
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler to prevent internal tracebacks leak to client (Security requirement)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please contact system support."}
    )

# Include core API routes
app.include_router(router)

# Mount static files for HTML/JS/CSS frontend
# Use absolute path to ensure mounting works regardless of execution context
public_dir = os.path.join(os.path.dirname(__file__), "public")
if not os.path.exists(public_dir):
    os.makedirs(public_dir)

app.mount("/", StaticFiles(directory=public_dir, html=True), name="public")


if __name__ == "__main__":
    # Start the server on port 8000
    uvicorn.run("run:app", host="0.0.0.0", port=8000, reload=True)
