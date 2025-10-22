# Backend Dockerfile for Production Deployment
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including ffmpeg for video processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables for ffmpeg binaries and Python output
ENV FFMPEG_BINARY=ffmpeg \
    FFPROBE_BINARY=ffprobe \
    PYTHONUNBUFFERED=1

# Create uploads directory
RUN mkdir -p uploads

# Copy and set permissions for startup script
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Expose port (Railway will set PORT env var)
EXPOSE 8000

# Run the application with dynamic PORT support
CMD ["/start.sh"]
