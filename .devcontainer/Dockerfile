ARG VARIANT="3.12-bullseye"
FROM mcr.microsoft.com/vscode/devcontainers/python:${VARIANT}

# Install basic packages, Node.js, and AWS CLI
RUN apt-get update && apt-get install -y \
    curl \
    vim \
    git \
    make \
    unzip \
    groff \
    less \
    iputils-ping \
    ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install AWS CLI v2
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf awscliv2.zip aws

# Install Claude Code globally
RUN npm install -g @anthropic-ai/claude-code

# Set working directory
WORKDIR /workspace
