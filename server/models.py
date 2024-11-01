from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base


class FileMetadata(Base):
    __tablename__ = "file_metadata"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    content_type = Column(String)
    file_size = Column(Integer)
    uploaded_size = Column(Integer, default=0)
    storage_path = Column(String)
    # possible values: "in_progress" | "completed"
    upload_status = Column(String, default="in_progress")
    created_at = Column(DateTime, server_default=func.now())
