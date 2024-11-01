# DataDock - File Upload Application

This project is a file upload application built using FastAPI (backend) and Next.js (frontend). It supports uploading single or multiple CSV files with real-time progress indication and resumable uploads. Uploaded files are stored in a cloud or local object storage, and file metadata is saved in a database. The application also provides file preview, download, and a list view of all uploaded files.

## Features

- **Upload CSV Files**: Supports single and multiple file uploads.
- **Resumable Uploads**: Allows resuming interrupted uploads.
- **Real-Time Progress**: Displays upload progress for each file.
- **File Preview and Download**: View the first few lines of each CSV file and download.
- **List of Uploaded Files**: View metadata and progress status for all uploaded files.

## Prerequisites

1. **Docker & Docker Compose**: Make sure Docker and Docker Compose are installed on your system.
2. **.env file**: The application requires environment variables for database connection and storage credentials.

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/datadock.git
   cd datadock

2. **Configure Environment Variables:** Create an .env file in the project root directory with the following variables:
   ```bash
   # Backend environment variables
    DATABASE_URL=sqlite:///./test.db
    MINIO_ROOT_USER=minioadmin
    MINIO_ROOT_PASSWORD=minioadmin

    # Frontend environment variables
    NEXT_PUBLIC_API_URL=http://localhost:8000

- MINIO_ROOT_USER and MINIO_ROOT_PASSWORD are MinIO storage credentials.
- DATABASE_URL specifies the database connection string.
- NEXT_PUBLIC_API_URL is the API base URL for the frontend.

3. **Set Up Docker Compose:** Docker Compose is configured to set up the FastAPI backend, Next.js frontend, and MinIO object storage
    ```bash
   docker-compose up --build
4. **Access the Application:**
   - Frontend: Open http://localhost:3000 in your browser to access the UI.
   - Backend API Documentation: Use http://localhost:8000 as the base URL for the APIs.

## Configuring Storage Credentials
1. **Local Storage with MinIO:** By default, the application uses MinIO for object storage, which can run locally through Docker.
2. **Configure MinIO Credentials:** In the .env file, add or update the following values with MinIO credentials:
    ```bash
    MINIO_ENDPOINT=minio:9000
    MINIO_ACCESS_KEY=minioadmin
    MINIO_SECRET_KEY=minioadmin

## Testing
### Cypress Tests (Frontend)

Run Cypress tests to validate the frontend functionality: 
1. Install Cypress dependencies:

    ```bash
    cd client
    npm install
2. Start the application (if not already running):

    ```bash
    docker-compose up
3. Run Cypress tests:

    ```bash
    npm run cypress:open

### Backend Tests (FastAPI)
For end-to-end API testing, use the built-in test framework with FastAPI.

1. Access postman collection at https://singleowner.postman.co/workspace/DataDock~d328e96c-8cab-41d7-aa98-a16bef8ea1fa/collection/24150770-86b5f1b8-fe8b-4e2f-a379-8fd62f88fcd4?action=share&creator=24150770 to try API endpoints.

## Additional Notes

1. **Error Handling:** The app includes basic error handling, such as validating file type and handling storage errors.
2. **Chunked Uploads:** Files are uploaded in chunks for efficient resumable uploads.
3. **Storage Configuration:** The app is set to use MinIO by default but can be configured for other storage solutions.
