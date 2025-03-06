FROM python:3.12-slim-bullseye

# Set working directory and create required directories
WORKDIR /app
RUN mkdir -p /app/images

# Install system dependencies using apt
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

# Copy source code first
COPY src ./src

# Copy in the personas - right now we mount in docker-compose
COPY personas /app/personas

# Copy agent_c_api pyproject.toml
COPY src/agent_c_api_ui/agent_c_api/pyproject.toml ./pyproject.toml

# Copy agent_c_api setup.py
COPY src/agent_c_api_ui/agent_c_api/setup.py ./setup.py

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Install Python dependencies
WORKDIR /app/src
RUN pip install -e agent_c_core \
    && pip install zep_cloud \
    && pip install -e agent_c_tools \
    && pip install -e my_agent_c \
    && pip install -e agent_c_reference_apps \
    && pip install -e agent_c_api_ui/agent_c_api

# Return to the app's root
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app
ENV ENHANCED_DEBUG_INFO="True"
ENV ENVIRONMENT="LOCAL_DEV"
ENV CLI_CHAT_USER_ID="Taytay"
ENV DALLE_IMAGE_SAVE_FOLDER="/app/images"

# Set the terminal type so the CLI UI works
ENV TERM=xterm-256color

# Set Selenium-related environment variables
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromium-driver

# Expose the FastAPI server port
EXPOSE 8000

# Command to run the API
CMD ["python", "-m", "uvicorn", "agent_c_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]