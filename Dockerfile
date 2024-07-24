FROM python:3.10

WORKDIR /bot

# Copy requirements and install them
COPY requirements.txt /bot/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the application
COPY . /bot

CMD ["python", "main.py"]
