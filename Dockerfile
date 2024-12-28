# Use NVIDIA's official CUDA image for Python and GPU support
FROM nvidia/cuda:12.6.3-base-ubuntu22.04
FROM python:3.11-slim

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Upgrade pip
RUN pip3 install --no-cache-dir --upgrade pip

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    ffmpeg \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the application code into the container
COPY *.py /app
COPY requirements.txt /app/requirements.txt
COPY transcripto /app/transcripto

# Install dependencies
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Default command (can be overridden)
CMD ["python3", "-m", "transcripto", "--telegram-bot"]
