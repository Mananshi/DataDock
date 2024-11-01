import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from main import app, FileMetadata
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set up the database for testing
DATABASE_URL = "sqlite:///./test.db"  # Use SQLite for tests
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def test_client():
    # Create the database tables
    FileMetadata.metadata.create_all(bind=engine)

    with TestClient(app) as client:
        yield client

    # Clean up the database after tests
    FileMetadata.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a new database session for a test."""
    db = TestingSessionLocal()
    yield db
    db.close()


def test_upload_file(test_client, db_session):
    """Test uploading a single file."""
    file_content = b"Test file content"
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file_content)
        tmp.seek(0)
        response = test_client.post(
            "/upload", files={"files": ("test.txt", tmp.read(), "text/plain")})

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["filename"] == "test.txt"
    assert response.json()[0]["status"] == "completed"
    assert response.json()[0]["uploaded_size"] == len(file_content)


def test_upload_multiple_files(test_client, db_session):
    """Test uploading multiple files."""
    files = [("file1.txt", b"Content of file 1"),
             ("file2.txt", b"Content of file 2")]
    responses = []

    for file_name, content in files:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(content)
            tmp.seek(0)
            response = test_client.post(
                "/upload", files={"files": (file_name, tmp.read(), "text/plain")})
            responses.append(response.json())

    assert all(response["status"] == "completed" for response in responses)
    assert len(responses) == 2


def test_get_upload_progress(test_client, db_session):
    """Test fetching upload progress for a file."""
    file_content = b"Test file content"
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file_content)
        tmp.seek(0)
        response = test_client.post(
            "/upload", files={"files": ("test.txt", tmp.read(), "text/plain")})

    filename = response.json()[0]["filename"]
    progress_response = test_client.get(f"/progress/{filename}")
    progress_data = progress_response.json()

    assert progress_response.status_code == 200
    assert progress_data["filename"] == filename
    assert progress_data["uploaded_size"] == len(file_content)
    assert progress_data["progress_percentage"] == 100.0


def test_get_all_upload_progress(test_client, db_session):
    """Test fetching progress for all uploaded files."""
    file_content = b"Test file content"
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file_content)
        tmp.seek(0)
        test_client.post(
            "/upload", files={"files": ("test.txt", tmp.read(), "text/plain")})

    response = test_client.get("/progress")
    progress_data = response.json()

    assert response.status_code == 200
    assert len(progress_data) > 0  # Check that there are uploaded files


def test_download_file(test_client, db_session):
    """Test downloading a file."""
    file_content = b"Test file content"
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file_content)
        tmp.seek(0)
        response = test_client.post(
            "/upload", files={"files": ("test.txt", tmp.read(), "text/plain")})

    filename = response.json()[0]["filename"]
    download_response = test_client.get(f"/download/{filename}")

    assert download_response.status_code == 200
    assert download_response.content == file_content


def test_download_nonexistent_file(test_client):
    """Test downloading a non-existent file."""
    download_response = test_client.get("/download/non_existent_file.txt")
    assert download_response.status_code == 404
    assert download_response.json()["detail"] == "File not found"


def test_preview_file(test_client, db_session):
    """Test previewing a file."""
    file_content = b"Line 1\nLine 2\nLine 3\nLine 4\nLine 5\nLine 6"
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file_content)
        tmp.seek(0)
        response = test_client.post(
            "/upload", files={"files": ("preview.txt", tmp.read(), "text/plain")})

    filename = response.json()[0]["filename"]
    preview_response = test_client.get(f"/preview/{filename}")
    preview_lines = preview_response.json()

    assert preview_response.status_code == 200
    assert len(preview_lines) == 5  # Ensure we get the first 5 lines


def test_get_progress_for_nonexistent_file(test_client):
    """Test fetching progress for a non-existent file."""
    progress_response = test_client.get("/progress/non_existent_file.txt")
    assert progress_response.status_code == 404
    assert progress_response.json()["detail"] == "File not found"


def test_get_progress_for_all_files(test_client, db_session):
    """Test fetching progress for all files."""
    file_content = b"Test file content"
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file_content)
        tmp.seek(0)
        test_client.post(
            "/upload", files={"files": ("test.txt", tmp.read(), "text/plain")})

    response = test_client.get("/progress")
    assert response.status_code == 200
    assert len(response.json()) > 0  # At least one file should be uploaded


if __name__ == "__main__":
    pytest.main()
