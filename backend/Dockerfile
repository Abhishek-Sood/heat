FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app
COPY alembic.ini ./
COPY migrations ./migrations
COPY start.sh ./
COPY setup_rag.py ./

# Make start script executable
RUN chmod +x start.sh

# Create directory for ChromaDB data
RUN mkdir -p /app/chroma_data

# Expose port (Render provides PORT env var)
EXPOSE 8000

# Use startup script that launches MCP server + FastAPI
CMD ["./start.sh"]
