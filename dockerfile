FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install system dependencies and add Microsoft key/repo
RUN apt-get update && \
    apt-get install -y gnupg curl apt-transport-https tzdata && \
    curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y \
        msodbcsql18 \
        unixodbc-dev \
        gcc \
        g++ \
        libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project files
COPY . .

EXPOSE 8000

# Use Gunicorn as the default command
CMD ["gunicorn", "connect_django.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
