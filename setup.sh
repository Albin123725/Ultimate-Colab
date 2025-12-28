#!/bin/bash
echo "🚀 Setting up Ultimate Colab Keeper..."

# Install Python dependencies
pip install -r requirements.txt

# Install Chrome
apt-get update
apt-get install -y wget gnupg
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
apt-get update
apt-get install -y google-chrome-stable

# Get ChromeDriver version
CHROME_VERSION=$(google-chrome --version | cut -d ' ' -f3)
echo "Chrome version: $CHROME_VERSION"

# Download matching ChromeDriver
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROME_VERSION}/chromedriver_linux64.zip"
unzip /tmp/chromedriver.zip -d /usr/local/bin/
chmod +x /usr/local/bin/chromedriver

echo "✅ Setup complete!"
