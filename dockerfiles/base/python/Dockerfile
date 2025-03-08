# Base Dockerfile for agent_c services
FROM python:3.12-slim

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TERM=xterm-256color
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromium-driver

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    git \
    vim \
    portaudio19-dev \
    python3-dev \
    libasound2-dev \
    ffmpeg \
    nodejs \
    npm \
    chromium \
    chromium-driver \
    cmake \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd -m agent_c

# Install Rust for agent_c user
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | su agent_c -c "sh -s -- -y"
ENV PATH="/home/agent_c/.cargo/bin:${PATH}"

# Create and set permissions for app directory
RUN mkdir -p /app && chown -R agent_c:agent_c /app

# Set the working directory
WORKDIR /app

# Copy requirements file and set correct ownership
COPY requirements.txt /tmp/
RUN chown agent_c:agent_c /tmp/requirements.txt

# Switch to the non-root user
USER agent_c

# Set up virtual environment as the non-root user
RUN python -m venv /home/agent_c/venv
ENV PATH="/home/agent_c/venv/bin:/home/agent_c/.cargo/bin:$PATH"

# Install Python dependencies inside the virtual environment
# Install packages with Rust dependencies first
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir tiktoken

# Then install the rest of the requirements
RUN pip install --no-cache-dir -r /tmp/requirements.txt || \
    pip install --no-cache-dir --no-binary=pyarrow -r /tmp/requirements.txt

# Set the entrypoint to the Python interpreter
#ENTRYPOINT ["python"]
