# Use Python 3.10 slim image as base
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies including Node.js
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Copy package.json files first for better caching
COPY frontend/package*.json ./frontend/
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Node.js dependencies and build frontend
WORKDIR /app/frontend
RUN npm install
COPY frontend/ ./
RUN npm run build

# Go back to app root
WORKDIR /app

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p data models

# Expose port 5000
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Run the Flask application
CMD ["python", "app.py"]
