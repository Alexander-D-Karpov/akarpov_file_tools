FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libmagic-dev \
    libjpeg-dev \
    zlib1g-dev \
    libimage-exiftool-perl \
    libmagickwand-dev \
    ffmpeg \
    libgdal-dev \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy and run the install script
COPY install_preview_dependencies.sh /app/
RUN chmod +x /app/install_preview_dependencies.sh && \
    /app/install_preview_dependencies.sh


COPY ./app /app/app

# Set up environment variables
ENV PREVIEW_CACHE_PATH=/tmp/preview_cache
RUN mkdir -p $PREVIEW_CACHE_PATH && chmod 777 $PREVIEW_CACHE_PATH

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]