ARG VARIANT="3.12-bullseye"
FROM mcr.microsoft.com/vscode/devcontainers/python:${VARIANT}

# Remove invalid Yarn repo (GPG key expired in base image)
RUN rm -f /etc/apt/sources.list.d/yarn.list

# Install basic packages and AWS CLI dependencies
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
    && rm -rf /var/lib/apt/lists/*

# Install AWS CLI v2
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf awscliv2.zip aws

# Install Claude Code using native installer (npm installation is deprecated)
RUN curl -fsSL https://claude.ai/install.sh | bash

# Ensure Claude Code binary is on PATH
ENV PATH="/root/.local/bin:${PATH}"

# Set working directory
WORKDIR /workspace
