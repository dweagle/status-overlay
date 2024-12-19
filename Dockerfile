# Stage 1: Build stage
FROM python:3.10-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
    gcc \
    python3-dev \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV TZ=UTC
ENV IN_DOCKER=true

# Configure timezone with fallback
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Set working directory
WORKDIR /app

# Upgrade pip to the latest version
RUN pip install --no-cache-dir --upgrade pip

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Copy fonts and application source code
COPY ./fonts /fonts
COPY ./scripts /app/scripts
COPY main.py .

# Stage 2: Runtime stage
FROM python:3.10-slim AS runtime

ENV TZ=UTC
ENV IN_DOCKER=true

# Configure timezone with fallback
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Set the working directory
WORKDIR /app

# Copy only the necessary files from the builder stage
COPY --from=builder /install /usr/local
COPY ./fonts /fonts
COPY ./scripts /app/scripts
COPY main.py .

ENV PYTHONPYCACHEPREFIX=/app/scripts/__pycache__

# Default entrypoint
ENTRYPOINT ["python3", "main.py"]
