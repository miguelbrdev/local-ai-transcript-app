# Use official Python 3.12 image as base
#FROM python:3.12-slim-bookworm

FROM nvidia/cuda:12.8.1-cudnn-runtime-ubuntu24.04



# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcublas12 \
    libcublaslt12 \
    python3.12 \
    python3.12-dev \
    python3-pip \
    python3.12-venv \
    curl \
    ca-certificates \
    git \
    # Minimal build deps for Python packages
    gcc \
    libc6-dev \
    && ln -sf /usr/bin/python3.12 /usr/bin/python \
    && ln -sf /usr/bin/python3.12 /usr/bin/python3 \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 24 LTS
RUN curl -fsSL https://deb.nodesource.com/setup_24.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm@latest \
    && rm -rf /var/lib/apt/lists/*

# Install uv system-wide
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && mv /root/.local/bin/uv /usr/local/bin/uv \
    && mv /root/.local/bin/uvx /usr/local/bin/uvx \
    && chmod +x /usr/local/bin/uv /usr/local/bin/uvx

# Verify installations
RUN python --version \
    && node --version \
    && npm --version \
    && uv --version

# Create non-root 'vscode' user to match docker-compose `user`
# If the user already exists this is a no-op.
RUN if ! id -u vscode >/dev/null 2>&1; then \
      groupadd -g 1000 vscode 2>/dev/null || true && \
      useradd -m -u 1000 -g 1000 -s /bin/bash vscode 2>/dev/null || true; \
    fi && \
    mkdir -p /workspaces/ai-transcript-app && chown -R vscode:vscode /workspaces || true

# Note: Previously the devcontainer common-utils feature created the non-root user.
