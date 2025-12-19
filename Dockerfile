# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY setup.py .
COPY presets/ ./presets/

# Install the package
RUN pip install --no-cache-dir -e .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port (Cloud Run will set $PORT)
EXPOSE 8080

# Set default environment variables
ENV MUSIC_GEN_MODE=simulate
ENV PORT=8080

# Run the API server
CMD uvicorn music_generator.api:app --host 0.0.0.0 --port ${PORT}
