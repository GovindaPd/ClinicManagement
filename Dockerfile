# Use official Python image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
# You can install extra packages via apt-get if needed:
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     libpq-dev \
#     && rm -rf /var/lib/apt/lists/*

# Copy requirements first (cache layer)
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project code
COPY . /app/

# -------- Create directories for volumes --------
RUN mkdir -p /app/static /app/media

# -------- Collect static files --------
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# -------- Default command (overridden by docker-compose) --------
# CMD ["gunicorn", "my_project.wsgi:application", "--bind", "0.0.0.0:8000"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]