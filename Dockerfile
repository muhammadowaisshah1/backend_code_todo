FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Render will use $PORT environment variable)
EXPOSE 8000

# Health check using curl (more lightweight than requests)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Start application (use PORT env var if available, otherwise 8000)
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
