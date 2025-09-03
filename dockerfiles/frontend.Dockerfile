FROM node:20-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    python3 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY src/agent_c_api_ui/agent_c_react_client/package*.json ./
COPY src/agent_c_api_ui/agent_c_react_client/scripts ./scripts/
RUN npm install

# Then copy the rest of the app
COPY src/agent_c_api_ui/agent_c_react_client/ ./
COPY agent_c_config /app/agent_c_config
# Set environment variables
ARG NODE_ENV=development
ENV NODE_ENV=${NODE_ENV}
ENV VITE_API_URL=https://localhost:8000/api/v1
ENV VITE_RAG_API_URL=https://localhost:8000/api/v1

# Expose the Vite dev server port
EXPOSE 5173

# Command to run development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]