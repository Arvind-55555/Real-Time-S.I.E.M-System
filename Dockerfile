FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy package files
COPY setup.py pyproject.toml requirements.txt ./
COPY src/ ./src/

# Install the package
RUN pip install --no-cache-dir -e .

# Create non-root user
RUN useradd --create-home --shell /bin/bash siem
USER siem

# Create necessary directories
RUN mkdir -p /home/siem/logs /home/siem/config

# Expose ports (adjust based on your application)
EXPOSE 5000 9200

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')"

CMD ["siem-start"]