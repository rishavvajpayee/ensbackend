# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make entrypoint script executable and fix line endings (if any)
RUN chmod +x docker-entrypoint.sh && \
    sed -i 's/\r$//' docker-entrypoint.sh 2>/dev/null || true

# Expose port
EXPOSE 8003

# Use entrypoint script with explicit bash
ENTRYPOINT ["/bin/bash", "./docker-entrypoint.sh"]

