# Use NVIDIA's official CUDA image for Python and GPU support
FROM nvidia/cuda:12.6.0-base-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-dev \
    libsndfile1 \
    ffmpeg \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

    # Ensure `python` points to `python3`
RUN ln -s /usr/bin/python3 /usr/bin/python

# Install PyTorch and other dependencies
COPY requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir --upgrade pip \
    && pip3 install --no-cache-dir -r /app/requirements.txt

# Copy the application code into the container
COPY . /app

# Default command (can be overridden)
CMD ["python3", "-m", "transcripto"]
