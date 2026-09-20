FROM python:3.12-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl && rm -rf /var/lib/apt/lists/*

# Install Node.js for building frontend (if needed)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && rm -rf /var/lib/apt/lists/*

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Build frontend if dist doesn't exist
RUN if [ ! -d "web/dist" ]; then cd web && npm install && npm run build; fi

# Expose port
EXPOSE 8000

# Run the server
CMD ["python", "run.py"]
