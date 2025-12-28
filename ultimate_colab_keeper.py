#!/usr/bin/env python3
"""
🚀 LIGHTWEIGHT COLAB KEEPER - Render.com Compatible
✅ NO Chrome/Selenium required
✅ HTTP requests only
✅ Works on free tier
✅ Simple and reliable
"""

import os
import time
import json
import logging
import threading
from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template_string
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LightweightColabKeeper:
    """Lightweight Colab keeper using HTTP requests only"""
    
    def __init__(self):
        self.is_running = False
        self.session = requests.Session()
        self.status = {
            "start_time": datetime.now(),
            "checks": 0,
            "successful": 0,
            "failed": 0,
            "last_check": None,
            "session_active": False
        }
        
        # Configuration
        self.colab_url = os.getenv("COLAB_URL", "")
        self.refresh_interval = int(os.getenv("REFRESH_INTERVAL", "300"))  # 5 minutes
        
        # Headers to mimic browser
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0"
        }
        
        if not self.colab_url:
            logger.error("❌ COLAB_URL environment variable not set!")
            logger.info("💡 Set in Render.com: COLAB_URL=https://colab.research.google.com/drive/YOUR_ID")
    
    def check_colab(self):
        """Check if Colab is accessible"""
        try:
            logger.info(f"🔍 Checking Colab: {self.colab_url[:50]}...")
            
            # Make request
            response = self.session.get(
                self.colab_url,
                headers=self.headers,
                timeout=30,
                allow_redirects=True
            )
            
            self.status["checks"] += 1
            self.status["last_check"] = datetime.now()
            
            # Check response
            if response.status_code == 200:
                self.status["successful"] += 1
                logger.info(f"✅ Colab accessible (Status: {response.status_code})")
                
                # Check for disconnection in response text
                if "disconnected" in response.text.lower():
                    logger.warning("⚠️ Colab shows disconnected state")
                    return False
                
                return True
            else:
                self.status["failed"] += 1
                logger.warning(f"⚠️ Colab check failed (Status: {response.status_code})")
                return False
                
        except requests.exceptions.Timeout:
            self.status["failed"] += 1
            logger.warning("⏰ Request timeout")
            return False
            
        except requests.exceptions.RequestException as e:
            self.status["failed"] += 1
            logger.warning(f"❌ Request error: {e}")
            return False
    
    def keep_alive(self):
        """Keep Colab alive by accessing it periodically"""
        logger.info("🚀 Starting keep-alive loop...")
        
        consecutive_failures = 0
        max_failures = 3
        
        while self.is_running:
            try:
                # Check Colab
                is_accessible = self.check_colab()
                
                if is_accessible:
                    consecutive_failures = 0
                    self.status["session_active"] = True
                else:
                    consecutive_failures += 1
                    self.status["session_active"] = False
                    
                    if consecutive_failures >= max_failures:
                        logger.error(f"🔥 {consecutive_failures} consecutive failures!")
                        # Could trigger notification here
                
                # Calculate next check time with jitter
                jitter = 0.8 + (0.4 * (time.time() % 1))  # Random between 0.8 and 1.2
                wait_time = self.refresh_interval * jitter
                
                logger.info(f"⏳ Next check in {int(wait_time)} seconds")
                time.sleep(wait_time)
                
            except KeyboardInterrupt:
                logger.info("🛑 Stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Unexpected error: {e}")
                time.sleep(60)
    
    def start(self):
        """Start the keeper"""
        if self.is_running:
            logger.warning("⚠️ Already running")
            return False
        
        logger.info("🚀 Starting Lightweight Colab Keeper")
        self.is_running = True
        self.status["start_time"] = datetime.now()
        
        # Start in background thread
        thread = threading.Thread(target=self.keep_alive, daemon=True)
        thread.start()
        
        logger.info("✅ Keeper started successfully")
        return True
    
    def stop(self):
        """Stop the keeper"""
        logger.info("🛑 Stopping keeper...")
        self.is_running = False
        
        # Calculate uptime
        uptime = datetime.now() - self.status["start_time"]
        
        logger.info(f"📊 Final Stats:")
        logger.info(f"   Uptime: {uptime}")
        logger.info(f"   Total Checks: {self.status['checks']}")
        logger.info(f"   Successful: {self.status['successful']}")
        logger.info(f"   Failed: {self.status['failed']}")
        
        return True

# Create Flask app
app = Flask(__name__)
keeper = LightweightColabKeeper()

# Dashboard
@app.route('/')
def dashboard():
    """Web dashboard"""
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Lightweight Colab Keeper</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }
            .header {
                text-align: center;
                margin-bottom: 40px;
            }
            .status-card {
                background: rgba(255, 255, 255, 0.15);
                padding: 25px;
                border-radius: 15px;
                margin-bottom: 25px;
            }
            .btn {
                background: #10b981;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                margin: 10px;
                transition: all 0.3s;
                width: 200px;
            }
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(0,0,0,0.2);
            }
            .btn-stop {
                background: #ef4444;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }
            .stat-box {
                background: rgba(255, 255, 255, 0.1);
                padding: 15px;
                border-radius: 10px;
                text-align: center;
            }
            .stat-value {
                font-size: 2em;
                font-weight: bold;
                margin: 10px 0;
            }
            .status-indicator {
                display: inline-block;
                width: 20px;
                height: 20px;
                border-radius: 50%;
                margin-right: 10px;
            }
            .status-running {
                background: #10b981;
                animation: pulse 2s infinite;
            }
            .status-stopped {
                background: #ef4444;
            }
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.5; }
                100% { opacity: 1; }
            }
        </style>
        <script>
            function updateStatus() {
                fetch('/api/status')
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('status').innerHTML = 
                            data.running ? 
                            '<span class="status-indicator status-running"></span>RUNNING' : 
                            '<span class="status-indicator status-stopped"></span>STOPPED';
                        document.getElementById('uptime').textContent = data.uptime;
                        document.getElementById('checks').textContent = data.checks;
                        document.getElementById('successful').textContent = data.successful;
                        document.getElementById('failed').textContent = data.failed;
                        document.getElementById('lastCheck').textContent = data.last_check || 'Never';
                        document.getElementById('colabUrl').textContent = data.colab_url;
                    });
            }
            
            function control(action) {
                fetch('/api/' + action)
                    .then(r => r.json())
                    .then(data => {
                        alert(data.message);
                        updateStatus();
                    });
            }
            
            // Auto-update every 3 seconds
            setInterval(updateStatus, 3000);
            window.onload = updateStatus;
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Lightweight Colab Keeper</h1>
                <p>Keep your Colab running 24/7 on Render.com</p>
            </div>
            
            <div class="status-card">
                <h2>Status: <span id="status">Loading...</span></h2>
                <div class="stats">
                    <div class="stat-box">
                        <div>Uptime</div>
                        <div class="stat-value" id="uptime">00:00:00</div>
                    </div>
                    <div class="stat-box">
                        <div>Total Checks</div>
                        <div class="stat-value" id="checks">0</div>
                    </div>
                    <div class="stat-box">
                        <div>Successful</div>
                        <div class="stat-value" id="successful">0</div>
                    </div>
                    <div class="stat-box">
                        <div>Failed</div>
                        <div class="stat-value" id="failed">0</div>
                    </div>
                </div>
                <p>Last Check: <span id="lastCheck">Never</span></p>
            </div>
            
            <div class="status-card">
                <h2>Controls</h2>
                <button class="btn" onclick="control('start')">▶️ Start Keeper</button>
                <button class="btn btn-stop" onclick="control('stop')">⏹️ Stop Keeper</button>
                <button class="btn" onclick="control('restart')">🔄 Restart</button>
            </div>
            
            <div class="status-card">
                <h2>Configuration</h2>
                <p><strong>Colab URL:</strong> <span id="colabUrl">Loading...</span></p>
                <p><strong>Check Interval:</strong> Every 5 minutes</p>
                <p><strong>Method:</strong> HTTP requests (No browser required)</p>
            </div>
            
            <div class="status-card">
                <h2>Quick Links</h2>
                <a href="/health" target="_blank"><button class="btn">Health Check</button></a>
                <a href="/api/status" target="_blank"><button class="btn">API Status</button></a>
                <a href="https://render.com" target="_blank"><button class="btn">Render.com</button></a>
            </div>
        </div>
    </body>
    </html>
    '''
    return html

# Health endpoint for UptimeRobot
@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "running": keeper.is_running,
        "timestamp": datetime.now().isoformat(),
        "service": "Lightweight Colab Keeper"
    })

# API endpoints
@app.route('/api/status')
def api_status():
    uptime = datetime.now() - keeper.status["start_time"] if keeper.status["start_time"] else timedelta(0)
    
    return jsonify({
        "running": keeper.is_running,
        "uptime": str(uptime).split('.')[0],
        "checks": keeper.status["checks"],
        "successful": keeper.status["successful"],
        "failed": keeper.status["failed"],
        "last_check": keeper.status["last_check"].isoformat() if keeper.status["last_check"] else None,
        "colab_url": keeper.colab_url[:50] + "..." if len(keeper.colab_url) > 50 else keeper.colab_url,
        "session_active": keeper.status["session_active"]
    })

@app.route('/api/start')
def api_start():
    if keeper.is_running:
        return jsonify({"message": "Already running", "success": True})
    
    success = keeper.start()
    return jsonify({
        "message": "Started successfully" if success else "Failed to start",
        "success": success
    })

@app.route('/api/stop')
def api_stop():
    if not keeper.is_running:
        return jsonify({"message": "Not running", "success": True})
    
    success = keeper.stop()
    return jsonify({
        "message": "Stopped successfully" if success else "Failed to stop",
        "success": success
    })

@app.route('/api/restart')
def api_restart():
    keeper.stop()
    time.sleep(2)
    success = keeper.start()
    return jsonify({
        "message": "Restarted successfully" if success else "Failed to restart",
        "success": success
    })

# Start function for Render.com
def start_app():
    """Start the application for Render.com"""
    logger.info("🚀 Starting Lightweight Colab Keeper on Render.com")
    
    # Start the keeper
    keeper.start()
    
    # Get port from environment
    port = int(os.getenv("PORT", 10000))
    
    # Start Flask app
    logger.info(f"🌍 Web dashboard available on port {port}")
    logger.info(f"🔗 Health check: https://your-app.onrender.com/health")
    logger.info(f"📊 Dashboard: https://your-app.onrender.com/")
    
    app.run(host='0.0.0.0', port=port, debug=False)

# Main entry point
if __name__ == "__main__":
    # Check if running on Render.com
    if os.getenv("RENDER"):
        start_app()
    else:
        # Local execution
        print("🚀 Starting Colab Keeper locally...")
        keeper.start()
        
        # Simple Flask server for local
        port = 8080
        print(f"🌍 Local dashboard: http://localhost:{port}")
        app.run(host='0.0.0.0', port=port, debug=True)
