from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home():
    return {
        "message": "Welcome to CareerAI!",
        "status": "Backend is running"
    }
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware


# =========================================================
# APP
# =========================================================

app = FastAPI(
    title="AI Resume Analyzer API",
    version="1.0.0"
)


# =========================================================
# CORS
# Allows your Live Server frontend to communicate
# with FastAPI during local development.
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5501",
        "http://localhost:5501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# UPLOAD DIRECTORY
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# SETTINGS
# =========================================================

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx"
}

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
}


# =========================================================
# ROOT / HEALTH CHECK
# =========================================================

@app.get("/")
def root():
    return {
        "message": "AI Resume Analyzer API is running",
        "status": "success"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# =========================================================
# RESUME UPLOAD
# =========================================================

@app.post("/upload-resume")
async def upload_resume(
    resume: UploadFile = File(...)
):

    # -----------------------------------------------------
    # 1. Check filename
    # -----------------------------------------------------

    if not resume.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected."
        )


    # -----------------------------------------------------
    # 2. Check extension
    # -----------------------------------------------------

    original_name = Path(resume.filename).name
    extension = Path(original_name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are allowed."
        )


    # -----------------------------------------------------
    # 3. Check MIME type when provided
    # -----------------------------------------------------

    if resume.content_type:
        if resume.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type."
            )


    # -----------------------------------------------------
    # 4. Read file
    # -----------------------------------------------------

    file_data = await resume.read()


    # -----------------------------------------------------
    # 5. Check file size
    # -----------------------------------------------------

    file_size = len(file_data)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size must be 5 MB or less."
        )


    if file_size == 0:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty."
        )


    # -----------------------------------------------------
    # 6. Generate unique filename
    # -----------------------------------------------------

    unique_name = f"{uuid4().hex}{extension}"

    file_path = UPLOAD_DIR / unique_name


    # -----------------------------------------------------
    # 7. Save file
    # -----------------------------------------------------

    try:

        file_path.write_bytes(file_data)

    except OSError as error:

        raise HTTPException(
            status_code=500,
            detail=f"Could not save file: {error}"
        )


    # -----------------------------------------------------
    # 8. Return response to frontend
    # -----------------------------------------------------

    return {
        "success": True,
        "message": "Resume uploaded successfully.",
        "original_filename": original_name,
        "stored_filename": unique_name,
        "size_bytes": file_size,
        "file_type": extension
    }