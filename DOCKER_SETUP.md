# Docker Setup for Smart Fleet Optimization App

This guide explains how to run your Smart Fleet Optimization project using Docker on your local machine.

---

## Prerequisites

- **Docker Desktop** installed and running

---

## Quick Start: Local Deployment

1. **Build the Docker image:**
   ```bash
   docker build -t smart-fleet-app .
   ```

2. **Run the container:**
   ```bash
   docker run -d -p 5000:5000 --name smart-fleet-container smart-fleet-app
   ```
   - The app will be available at [http://localhost:5000](http://localhost:5000)
   - Both frontend and backend are served on the same port (5000)

3. **Stop and remove the container:**
   ```bash
   docker stop smart-fleet-container
   docker rm smart-fleet-container
   ```

---

## (Optional) Using the Batch Script (Windows)

You can use `run_docker.bat` to automate the build and run process:
```bash
run_docker.bat
```

---

## Troubleshooting

- **Port already in use:** Stop/remove any existing container with the same name.
- **View logs:**  
  ```bash
  docker logs smart-fleet-container
  ```
- **Remove unused images/containers:**  
  ```bash
  docker system prune
  ```

---

## Health Check

The application includes a health check endpoint:

Returns: `{"status": "ok"}`

---

## Need Help?

If you have any issues running the project locally with Docker, please ask for help!