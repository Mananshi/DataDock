from fastapi import FastAPI, UploadFile, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from minio import Minio
from models import FileMetadata
from database import get_db, Base, engine
import os
import io

from sqlalchemy.exc import IntegrityError
from starlette.responses import StreamingResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MinIO client
minio_client = Minio(
    "minio:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False,
)


# Ensure bucket creation
def ensure_bucket(bucket_name):
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)


# Create the database tables
Base.metadata.create_all(bind=engine)


# Helper function to upload file chunks
async def upload_chunk(file, bucket_name, file_path, chunk, db, file_metadata):
    chunk_size = len(chunk)
    chunk_stream = io.BytesIO(chunk)
    minio_client.put_object(bucket_name, file_path,
                            data=chunk_stream, length=chunk_size)

    # Update uploaded size in the database
    file_metadata.uploaded_size += chunk_size
    db.commit()


@app.post("/upload")
async def upload_files(files: list[UploadFile], db: Session = Depends(get_db)):
    ensure_bucket("uploads")
    responses = []
    CHUNK_SIZE = 1024 * 1024  # 1 MB chunks

    for file in files:
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400, detail="Only .csv files are allowed")
        # Check for existing metadata to resume uploads
        existing_metadata = db.query(FileMetadata).filter(
            FileMetadata.filename == file.filename).first()

        if existing_metadata:
            # If metadata exists, check uploaded size
            file_metadata = existing_metadata
        else:
            file.file.seek(0, 2)
            file_size = file.file.tell()
            file.file.seek(0)

            file_metadata = FileMetadata(
                filename=file.filename,
                content_type=file.content_type,
                file_size=file_size,
                storage_path=f"uploads/{file.filename}",
                uploaded_size=0,
                upload_status="in_progress"
            )
            db.add(file_metadata)
            db.commit()
            db.refresh(file_metadata)

        file.file.seek(file_metadata.uploaded_size)
        # Start chunked upload
        while file_metadata.uploaded_size < file_metadata.file_size:
            # Read the next chunk
            remaining_size = file_metadata.file_size - file_metadata.uploaded_size
            chunk_size = min(CHUNK_SIZE, remaining_size)
            chunk = file.file.read(chunk_size)

            if not chunk:
                break  # End of file

            # Upload the chunk to Minio
            await upload_chunk(
                file,
                bucket_name="uploads",
                file_path=file_metadata.storage_path,
                chunk=chunk,
                db=db,
                file_metadata=file_metadata
            )

        # Update status after upload completion
        if file_metadata.uploaded_size >= file_metadata.file_size:
            file_metadata.upload_status = "completed"
        db.commit()

        responses.append({
            "id": file_metadata.id,
            "filename": file.filename,
            "status": file_metadata.upload_status,
            "uploaded_size": file_metadata.uploaded_size,
            "file_size": file_size,
        })

    return responses


@app.get("/download/{file_id}")
async def download_file(file_id: int, db: Session = Depends(get_db)):
    file_metadata = db.query(FileMetadata).filter(
        FileMetadata.id == file_id).first()
    if not file_metadata:
        raise HTTPException(status_code=404, detail="File not found")

    try:
        response = minio_client.get_object(
            "uploads", file_metadata.storage_path)

        headers = {
            "Content-Disposition": f"attachment; filename={file_metadata.filename}",
            "Content-Type": file_metadata.content_type
        }

        return StreamingResponse(response, media_type="text/csv", headers=headers)
    except Exception as e:
        raise HTTPException(status_code=404, detail="File not found")


@app.get("/files")
async def list_files(db: Session = Depends(get_db)):
    files = db.query(FileMetadata).all()
    return [{
        "id": file.id,
        "filename": file.filename,
        "uploaded_size": file.uploaded_size,
        "file_size": file.file_size,
        "status": file.upload_status
    } for file in files]


@app.get("/preview/{file_id}")
async def preview_file(file_id: int, db: Session = Depends(get_db)):
    file_metadata = db.query(FileMetadata).filter(
        FileMetadata.id == file_id).first()
    if not file_metadata:
        raise HTTPException(status_code=404, detail="File not found")

    try:
        response = minio_client.get_object(
            "uploads", file_metadata.storage_path)
        lines = response.read().decode().splitlines()
        return lines[:5]
    except Exception:
        raise HTTPException(status_code=404, detail="File not found")


@app.get("/progress/{file_id}")
async def get_upload_progress(file_id: int, db: Session = Depends(get_db)):
    file_metadata = db.query(FileMetadata).filter(
        FileMetadata.id == file_id).first()
    if not file_metadata:
        raise HTTPException(status_code=404, detail="File not found")

    progress = {
        "id": file_metadata.id,
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
