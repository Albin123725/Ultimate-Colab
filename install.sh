#!/bin/bash
echo "🚀 Installing AI Colab Supreme Bot..."

# Update system
apt-get update
apt-get upgrade -y

# Install system dependencies
apt-get install -y \
    wget \
    curl \
    gnupg \
    unzip \
    python3.11 \
    python3-pip \
    python3-venv \
    tesseract-ocr \
    libtesseract-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libxcomposite1 \
    libxi6 \
    libxtst6 \
    libnss3 \
    libgconf-2-4 \
    libxss1 \
    libasound2 \
    fonts-liberation

# Install Chrome
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
apt-get update
apt-get install -y google-chrome-stable

# Install ChromeDriver
CHROME_VERSION=$(google-chrome --version | cut -d ' ' -f3 | cut -d '.' -f1)
CHROME_DRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}")
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROME_DRIVER_VERSION}/chromedriver_linux64.zip"
unzip /tmp/chromedriver.zip -d /usr/local/bin/
chmod +x /usr/local/bin/chromedriver
rm /tmp/chromedriver.zip

# Create Python environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install flask flask-socketio prometheus_client psutil selenium undetected-chromedriver

# Install AI dependencies (optional)
read -p "Install AI dependencies? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    pip install numpy opencv-python pillow pytesseract ultralytics openai scikit-learn pandas
    echo "✅ AI dependencies installed"
else
    echo "⚠️ AI features will be disabled"
fi

# Create directories
mkdir -p logs screenshots models

# Create .env file if not exists
if [ ! -f .env ]; then
    cat > .env << EOL
# Colab URL
COLAB_URL=https://colab.research.google.com/drive/YOUR_NOTEBOOK_ID

# AI Settings (optional)
OPENAI_API_KEY=your_key_here
ENABLE_AI=true
ENABLE_CV=true

# Bot Settings
MAX_PARALLEL_TABS=3
CHECK_INTERVAL=150
HEADLESS=true

# Telegram (optional)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
ENABLE_TELEGRAM=false

# Monitoring
LOG_LEVEL=INFO
ENABLE_LOGGING=true
EOL
    echo "📁 Created .env file. Please update your Colab URL!"
fi

# Make script executable
chmod +x ai_colab_supreme_final.py

echo "✅ Installation complete!"
echo "📝 Next steps:"
echo "1. Edit .env file with your Colab URL"
echo "2. Run: python ai_colab_supreme_final.py"
echo "3. Open browser to: http://localhost:8080"
