#!/bin/bash
echo "🔧 Setting up Colab Keeper on Render.com..."

# Install system dependencies
apt-get update
apt-get install -y wget gnupg unzip

# Install Chrome
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
apt-get update
apt-get install -y google-chrome-stable

# Install Chromium as fallback
apt-get install -y chromium chromium-driver

echo "✅ Setup complete"
