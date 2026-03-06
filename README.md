# Petroleum Batchtrack System

A real-time petroleum batch tracking system for pipeline management, containerized with Docker and served via Uvicorn.

## Features
- **Real-time Visualization**: Track batch positions along the pipeline.
- **Batch Management**: Create and track petroleum product batches.
- **Flow Entry Tracking**: Monitor hourly flow volumes and movement.
- **Containerized Architecture**: Easy deployment using Docker and Docker Compose.
- **Modern Tech Stack**: FastAPI (Backend), React + Vite (Frontend), SQLite (Database).

## Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

## Local Setup & Execution

### 1. Clone the repository (if not already local)
```bash
git clone https://github.com/amblonzi/Petroleum-Batchtrack-System.git
cd Petroleum-Batchtrack-System
```

### 2. Start the system with Docker Compose
Run the following command in the root directory:
```powershell
docker-compose up --build -d
```
This will build the frontend and backend images and start the containers in detached mode.

### 3. Initialize the Database
Once the containers are running, you need to seed the database with admin credentials and initial data:
```powershell
docker exec batchtrack_backend uv run python init_db.py
```

### 4. Access the Application
- **Frontend (UI)**: [http://localhost:3000](http://localhost:3000)
- **Backend (API Docs)**: [http://localhost:8001/docs](http://localhost:8001/docs)

## Credentials
- **Username**: `admin`
- **Password**: `admin123`

## Configuration
Ports are configured in `docker-compose.yml` to avoid common conflicts:
- **Frontend**: 3000
- **Backend**: 8001
