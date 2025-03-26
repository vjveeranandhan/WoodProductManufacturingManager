FROM python:3.10.12-slim-buster

WORKDIR /app

# Install PostgreSQL dependencies
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt requirements.txt

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose the application port
EXPOSE 8000

# Start the application
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000", "--noreload"]
