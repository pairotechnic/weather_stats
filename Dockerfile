# Use slim Python Image
FROM python:3.10-slim

# Prevents Python from buffering stdout/stderr
ENV PYTHONBUFFERRED 1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files (optional in dev)
RUN python manage.py collectstatic --noinput || true

# Default command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]