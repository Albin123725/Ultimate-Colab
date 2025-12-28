#!/usr/bin/env python3
"""
🚀 24/7 COLAB KEEPER - SIMPLE & EFFECTIVE
✅ Pings Colab every 3 minutes
✅ Prevents 90-minute timeout
✅ Works when laptop closed
✅ Dashboard for monitoring
"""

import os
import time
import logging
import threading
from datetime import datetime
from flask import Flask, jsonify, render_template_string
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ColabKeeper:
    def __init__(self):
        self.is_running = False
        self.session = requests.Session()
        self.start_time = datetime.now()
        
        # Get Colab URL from environment
        self.colab_url = os.getenv("COLAB_URL", "")
        
        # Statistics
        self.stats = {
            "total_pings": 0,
            "successful_pings": 0,
            "failed_pings": 0,
            "last_check": None,
            "start_time": self.start_time
        }
        
        # Browser-like headers
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
        if not self.colab_url:
            logger.error("❌ COLAB_URL environment variable not set!")
            logger.info("💡 Set in Render.com: COLAB_URL=https://colab.research.google.com/drive/YOUR_ID")
        else:
            logger.info(f"✅ Colab URL: {self.colab_url[:50]}...")
    
    def ping_colab(self):
        """Ping Colab to reset idle timer"""
        try:
            logger.info("🔍 Pinging Colab...")
            
            response = self.session.get(
                self.colab_url,
                headers=self.headers,
                timeout=30,
                allow_redirects=True
            )
            
            self.stats["total_pings"] += 1
            self.stats["last_check"] = datetime.now()
            
            if response.status_code == 200:
                self.stats["successful_pings"] += 1
                logger.info(f"✅ Ping successful (Status: {response.status_code})")
                
                # Check if Colab shows disconnected
                if "disconnected" in response.text.lower():
                    logger.warning("⚠️ Colab shows 'disconnected' - may need manual reconnect")
                    return "disconnected"
                return "active"
            else:
                self.stats["failed_pings"] += 1
                logger.warning(f"⚠️ Ping failed (Status: {response.status_code})")
                return "failed"
                
        except requests.exceptions.Timeout:
            self.stats["failed_pings"] += 1
            logger.warning("⏰ Request timeout")
            return "timeout"
            
        except requests.exceptions.RequestException as e:
            self.stats["failed_pings"] += 1
            logger.warning(f"❌ Request error: {e}")
            return "error"
    
    def keep_alive_loop(self):
        """Main loop that keeps Colab alive"""
        logger.info("🚀 Starting 24/7 keep-alive loop...")
        
        consecutive_failures = 0
        
        while self.is_running:
            try:
                # Ping Colab
                status = self.ping_colab()
                
                if status == "active":
                    consecutive_failures = 0
                    logger.info("✅ Colab is active")
                else:
                    consecutive_failures += 1
                    logger.warning(f"⚠️ Ping status: {status} (Failures: {consecutive_failures})")
                    
                    if consecutive_failures >= 3:
                        logger.error("🔥 Multiple consecutive failures!")
                        consecutive_failures = 0
                
                # Wait for next ping (3 minutes with random jitter)
                wait_time = 180 + (time.time() % 60)  # 180-240 seconds
                logger.info(f"⏳ Next ping in {int(wait_time)} seconds")
                time.sleep(wait_time)
                
            except Exception as e:
                logger.error(f"❌ Loop error: {e}")
                time.sleep(60)
    
    def start(self):
        """Start the keeper"""
        if self.is_running:
            logger.warning("⚠️ Already running")
            return False
        
        logger.info("🚀 Starting Colab Keeper")
        self.is_running = True
        
        # Start in background thread
        thread = threading.Thread(target=self.keep_alive_loop, daemon=True)
        thread.start()
        
        logger.info("✅ Keeper started successfully")
        return True
    
    def stop(self):
        """Stop the keeper"""
        logger.info("🛑 Stopping keeper...")
        self.is_running = False
        
        # Calculate uptime
        uptime = datetime.now() - self.start_time
        
        logger.info("📊 Final Statistics:")
        logger.info(f"   Uptime: {uptime}")
        logger.info(f"   Total Pings: {self.stats['total_pings']}")
        logger.info(f"   Successful: {self.stats['successful_pings']}")
        logger.info(f"   Failed: {self.stats['failed_pings']}")
        
        return True

# Create Flask app
app = Flask(__name__)
bot = ColabKeeper()

# Web Dashboard
@app.route('/')
def dashboard():
    """Main dashboard"""
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>24/7 Colab Keeper</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
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
            .card {
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
            }
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(0,0,0,0.2);
            }
            .btn-stop {
                background: #ef4444;
            }
            .stats-grid {
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
            .status-running {
                color: #10b981;
                font-weight: bold;
            }
            .status-stopped {
                color: #ef4444;
                font-weight: bold;
            }
        </style>
        <script>
            function updateStatus() {
                fetch('/api/status')
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('status').innerHTML = 
                            data.running ? 
                            '<span class="status-running">🟢 RUNNING</span>' : 
                            '<span class="status-stopped">🔴 STOPPED</span>';
                        
                        document.getElementById('totalPings').textContent = data.total_pings;
                        document.getElementById('successful').textContent = data.successful_pings;
                        document.getElementById('failed').textContent = data.failed_pings;
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
            
            // Auto-update every 5 seconds
            setInterval(updateStatus, 5000);
            window.onload = updateStatus;
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 24/7 Colab Keeper</h1>
                <p>Keeps your Colab running even when laptop is closed</p>
            </div>
            
            <div class="card">
                <h2>Status: <span id="status">Loading...</span></h2>
                <div class="stats-grid">
                    <div class="stat-box">
                        <div>Total Pings</div>
                        <div class="stat-value" id="totalPings">0</div>
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
                <p>Colab URL: <span id="colabUrl">Loading...</span></p>
            </div>
            
            <div class="card">
                <h2>Controls</h2>
                <button class="btn" onclick="control('start')">▶️ Start Keeper</button>
                <button class="btn btn-stop" onclick="control('stop')">⏹️ Stop Keeper</button>
                <button class="btn" onclick="updateStatus()">🔄 Refresh Status</button>
            </div>
            
            <div class="card">
                <h2>How It Works</h2>
                <p>✅ Pings your Colab every 3 minutes</p>
                <p>✅ Prevents 90-minute idle timeout</p>
                <p>✅ Runs on Render.com 24/7</p>
                <p>✅ Works when laptop/browser closed</p>
                <p>⚠️ Note: Colab has 12-hour limit (needs manual restart)</p>
            </div>
            
            <div class="card">
                <h2>Quick Links</h2>
                <a href="/health" target="_blank"><button class="btn">Health Check</button></a>
                <a href="/api/status" target="_blank"><button class="btn">API Status</button></a>
                <a href="''' + (bot.colab_url if bot.colab_url else "https://colab.research.google.com") + '''" target="_blank"><button class="btn">Open Colab</button></a>
            </div>
        </div>
    </body>
    </html>
    '''
    return html

# Health endpoint for monitoring
@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "running": bot.is_running,
        "timestamp": datetime.now().isoformat()
    })

# API endpoints
@app.route('/api/status')
def api_status():
    return jsonify({
        "running": bot.is_running,
        "total_pings": bot.stats["total_pings"],
        "successful_pings": bot.stats["successful_pings"],
        "failed_pings": bot.stats["failed_pings"],
        "last_check": bot.stats["last_check"].isoformat() if bot.stats["last_check"] else None,
        "colab_url": bot.colab_url[:50] + "..." if len(bot.colab_url) > 50 else bot.colab_url
    })

@app.route('/api/start')
def api_start():
    if bot.is_running:
        return jsonify({"message": "Already running", "success": True})
    
    success = bot.start()
    return jsonify({
        "message": "Keeper started" if success else "Failed to start",
        "success": success
    })

@app.route('/api/stop')
def api_stop():
    if not bot.is_running:
        return jsonify({"message": "Not running", "success": True})
    
    success = bot.stop()
    return jsonify({
        "message": "Keeper stopped" if success else "Failed to stop",
        "success": success
    })

# Main function
def main():
    print("\n" + "="*60)
    print("🚀 24/7 COLAB KEEPER")
    print("="*60)
    
    if bot.colab_url:
        print(f"📓 Colab URL: {bot.colab_url[:50]}...")
    else:
        print("❌ No Colab URL set!")
        print("💡 Set COLAB_URL environment variable on Render.com")
    
    print("="*60)
    
    # Auto-start on Render.com
    if os.getenv("RENDER"):
        print("🌐 Render.com detected - Auto-starting...")
        bot.start()
        
        port = int(os.getenv("PORT", 10000))
        print(f"🌍 Dashboard: http://0.0.0.0:{port}")
        print(f"🔗 Health Check: https://your-app.onrender.com/health")
        
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        # Local execution
        print("💻 Local execution")
        bot.start()
        
        port = 8080
        print(f"🌍 Local dashboard: http://localhost:{port}")
        app.run(host='0.0.0.0', port=port, debug=True)

if __name__ == "__main__":
    main()
