# Use a specific version of Python to avoid compatibility issues
FROM python:3.10

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /bot

# Copy requirements and install them
COPY requirements.txt /bot/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the application
COPY . /bot

# Set the command to run the application
CMD ["python", "main.py"]
