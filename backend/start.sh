#!/bin/bash

# Use Railway's PORT environment variable or default to 8000
PORT=${PORT:-8000}

# Start uvicorn with the dynamic port
uvicorn app.main:app --host 0.0.0.0 --port $PORT
