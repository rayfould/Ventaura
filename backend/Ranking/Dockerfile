FROM python:3.11-slim
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py ./         
COPY services.py RBS.py models.py config.py quicksort.py ./

# Expose port (configurable via PORT env var, default 8000)
EXPOSE 8000

# Environment variables will be provided by docker-compose from .env file
# Run uvicorn with port from environment variable (default 8000)
CMD uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}