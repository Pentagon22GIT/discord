FROM python:3.10

WORKDIR /bot

# Install build dependencies
RUN apt-get update && apt-get install -y build-essential

# Copy requirements and install them
COPY requirements.txt /bot/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . /bot

CMD ["python", "main.py"]
