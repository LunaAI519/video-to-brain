# video-to-brain — Multi-stage Docker build
# Usage: docker compose up -d

FROM python:3.12-slim AS base

# Install ffmpeg (required for audio extraction)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create default cache and vault directories
RUN mkdir -p /data/vault /data/cache

# Default environment
ENV OBSIDIAN_VAULT=/data/vault
ENV PYTHONUNBUFFERED=1

EXPOSE 8443

CMD ["python", "bot.py"]
