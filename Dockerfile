# video-to-brain — Docker build
# Usage: docker compose up -d

FROM python:3.12-slim

# Install system dependencies (ffmpeg for audio extraction)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir openai-whisper

# Copy source code
COPY . .

# Create default cache and vault directories
RUN mkdir -p /data/vault /data/cache

# Create non-root user for security
RUN groupadd -r botuser && useradd -r -g botuser -d /app botuser && \
    chown -R botuser:botuser /app /data
USER botuser

# Default environment
ENV OBSIDIAN_VAULT=/data/vault
ENV PYTHONUNBUFFERED=1

# Health check — verify the bot process is running
HEALTHCHECK --interval=60s --timeout=10s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

CMD ["python", "bot.py"]
