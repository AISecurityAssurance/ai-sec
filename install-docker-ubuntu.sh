#!/bin/bash

# Docker installation script for Ubuntu
set -e

echo "🐳 Installing Docker on Ubuntu"
echo "=============================="

# Update package index
echo "Updating package index..."
sudo apt-get update

# Install prerequisites
echo "Installing prerequisites..."
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
echo "Adding Docker GPG key..."
sudo mkdir -m 0755 -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up the repository
echo "Setting up Docker repository..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package index again
echo "Updating package index with Docker repository..."
sudo apt-get update

# Install Docker Engine
echo "Installing Docker Engine..."
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add current user to docker group (to run without sudo)
echo "Adding $USER to docker group..."
sudo usermod -aG docker $USER

# Start and enable Docker
echo "Starting Docker service..."
sudo systemctl start docker
sudo systemctl enable docker

# Verify installation
echo "Verifying Docker installation..."
sudo docker run hello-world

echo ""
echo "✅ Docker installation complete!"
echo ""
echo "⚠️  IMPORTANT: You need to log out and back in for group changes to take effect."
echo "   After logging back in, you can run docker commands without sudo."
echo ""
echo "To test after re-login:"
echo "  docker run hello-world"
echo "  docker compose version"