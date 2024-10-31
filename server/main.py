from fastapi import FastAPI, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from minio import Minio
from models import FileMetadata
from database import get_db, Base, engine
import os

from sqlalchemy.exc import IntegrityError
from starlette.responses import StreamingResponse

app = FastAPI()

# Initialize MinIO client
minio_client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False,
)

# Create the database tables
Base.metadata.create_all(bind=engine)


# Helper function to upload file chunks
def upload_chunk(file, bucket_name, file_path, offset):
    chunk = file.file.read(offset)
    minio_client.put_object(bucket_name, file_path,
                            data=chunk, length=len(chunk))
    return len(chunk)


@app.post("/upload")
async def upload_files(files: list[UploadFile], db: Session = Depends(get_db)):
    responses = []
    for file in files:
        file_metadata = db.query(FileMetadata).filter(
            FileMetadata.filename == file.filename).first()

        # If no metadata exists, create a new entry
        if not file_metadata:
            file_metadata = FileMetadata(
                filename=file.filename,
                content_type=file.content_type,
                file_size=file.file.size,  # Adjusted to read the actual size
                storage_path=f"bucket_name/{file.filename}"
            )
            db.add(file_metadata)
            db.commit()
        else:
            # Set the file size if it exists (this is essential for progress tracking)
            file_metadata.file_size = max(
                file_metadata.file_size, file.file.size)

        # Calculate offset for resumable upload
        offset = file_metadata.uploaded_size
        chunk_size = 10 * 1024 * 1024  # 10MB chunk size

        # Read the file in chunks and upload
        while offset < file_metadata.file_size:
            file.file.seek(offset)  # Move to the offset
            chunk = file.file.read(chunk_size)
            if not chunk:  # Break if there's nothing left to read
                break
            uploaded_bytes = upload_chunk(
                file, "bucket_name", file_metadata.storage_path, chunk)
            file_metadata.uploaded_size += uploaded_bytes
            offset += uploaded_bytes

        # Update upload status
        if file_metadata.uploaded_size >= file_metadata.file_size:
            file_metadata.upload_status = "completed"
        db.commit()

        responses.append({
            "filename": file.filename,
            "status": file_metadata.upload_status,
            "uploaded_size": file_metadata.uploaded_size,
            "file_size": file_metadata.file_size,
        })
    return responses


@app.get("/download/{filename}")
async def download_file(filename: str):
    try:
        response = minio_client.get_object("bucket_name", filename)
        return StreamingResponse(response, media_type="application/octet-stream")
    except Exception as e:
        raise HTTPException(status_code=404, detail="File not found")


@app.get("/files")
async def list_files(db: Session = Depends(get_db)):
    files = db.query(FileMetadata).all()
    return [{"filename": file.filename, "uploaded_size": file.uploaded_size, "file_size": file.file_size, "status": file.upload_status} for file in files]


@app.get("/preview/{filename}")
async def preview_file(filename: str):
    try:
        response = minio_client.get_object("bucket_name", filename)
        # Read the first few lines for preview
        lines = response.read().decode().splitlines()
        return lines[:5]  # Return the first 5 lines for preview
    except Exception as e:
        raise HTTPException(status_code=404, detail="File not found")


@app.get("/progress/{filename}")
async def get_upload_progress(filename: str, db: Session = Depends(get_db)):
    file_metadata = db.query(FileMetadata).filter(
        FileMetadata.filename == filename).first()

    if not file_metadata:
        raise HTTPException(status_code=404, detail="File not found")

    progress = {
        "filename": file_metadata.filename,
        "uploaded_size": file_metadata.uploaded_size,
        "file_size": file_metadata.file_size,
        "progress_percentage": (file_metadata.uploaded_size / file_metadata.file_size * 100) if file_metadata.file_size > 0 else 0,
        "status": file_metadata.upload_status,
    }

    return progress


@app.get("/progress")
async def get_all_upload_progress(db: Session = Depends(get_db)):
    all_files_metadata = db.query(FileMetadata).all()

    progress_list = []
    for file_metadata in all_files_metadata:
        progress = {
            "filename": file_metadata.filename,
            "uploaded_size": file_metadata.uploaded_size,
            "file_size": file_metadata.file_size,
            "progress_percentage": (file_metadata.uploaded_size / file_metadata.file_size * 100) if file_metadata.file_size > 0 else 0,
            "status": file_metadata.upload_status,
        }
        progress_list.append(progress)

    return progress_list
