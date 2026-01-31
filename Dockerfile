# Dockerfile for Rice Quality System Backend
FROM node:18-slim

# Install Python and dependencies for AI inference
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy backend package files
COPY backend/package*.json ./backend/
WORKDIR /app/backend
RUN npm install

# Copy AI requirements and setup venv
WORKDIR /app
COPY ai/requirements.txt ./ai/
RUN python3 -m venv ai/venv && \
    ./ai/venv/bin/pip install --upgrade pip && \
    ./ai/venv/bin/pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    ./ai/venv/bin/pip install ultralytics && \
    ./ai/venv/bin/pip install -r ai/requirements.txt

# Copy the rest of the application
COPY backend ./backend
COPY ai ./ai
COPY runs ./runs

# Create uploads directory
RUN mkdir -p /app/backend/uploads

# Expose port
EXPOSE 3000

# Set working directory to backend
WORKDIR /app/backend

# Start the server
CMD ["node", "index.js"]
