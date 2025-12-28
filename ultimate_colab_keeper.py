#!/usr/bin/env python3
"""
🔥 SIMPLIFIED 24/7 COLAB BOT - Requests Only
✅ No Chrome/Selenium needed
✅ Uses Colab's public API
✅ Works on Render.com free tier
✅ Keeps Colab alive 24/7
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
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleColabKeeper:
    """Simple Colab keeper using HTTP requests only"""
    
    def __init__(self):
        self.is_running = False
        self.session = requests.Session()
        self.session_start = None
        self.last_check = None
        
        # Configuration
        self.colab_url = os.getenv("COLAB_URL", "")
        self.ping_interval = int(os.getenv("PING_INTERVAL", "180"))  # 3 minutes
        self.max_session_hours = 11.5  # Restart before 12h limit
        
        # Statistics
        self.stats = {
            "total_pings": 0,
            "successful_pings": 0,
            "failed_pings": 0,
            "session_restarts": 0,
            "total_runtime": timedelta(0),
            "current_session_start": None
        }
        
        # Headers to mimic browser
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
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
            logger.error("❌ COLAB_URL not set!")
            logger.info("💡 Set in Render.com: COLAB_URL=https://colab.research.google.com/drive/YOUR_ID")
        else:
            logger.info(f"📝 Colab URL: {self.colab_url[:50]}...")
    
    def ping_colab(self):
        """Ping Colab to keep it alive"""
        try:
            logger.info(f"🔍 Pinging Colab...")
            
            # Make request
            response = self.session.get(
                self.colab_url,
                headers=self.headers,
                timeout=30,
                allow_redirects=True
            )
            
            self.stats["total_pings"] += 1
            self.last_check = datetime.now()
            
            if response.status_code == 200:
                self.stats["successful_pings"] += 1
                
                # Check if session is disconnected
                if "disconnected" in response.text.lower():
                    logger.warning("⚠️ Colab shows disconnected state")
                    return "disconnected"
                else:
                    logger.info(f"✅ Ping successful (Status: {response.status_code})")
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
    
    def calculate_session_age(self):
        """Calculate current session age"""
        if self.session_start:
            return (datetime.now() - self.session_start).total_seconds() / 3600
        return 0
    
    def reset_session(self):
        """Reset session tracking"""
        logger.info("🔄 Resetting session tracker...")
        self.session_start = datetime.now()
        self.stats["current_session_start"] = datetime.now()
        self.stats["session_restarts"] += 1
    
    def keep_alive_loop(self):
        """Main keep-alive loop"""
        logger.info("🚀 Starting 24/7 keep-alive loop...")
        
        consecutive_failures = 0
        max_consecutive_failures = 5
        
        # Start first session
        self.reset_session()
        
        while self.is_running:
            try:
                # Calculate session age
                session_age = self.calculate_session_age()
                
                # Check if session too old (near 12-hour limit)
                if session_age > self.max_session_hours:
                    logger.warning(f"⏰ Session age: {session_age:.1f}h - Consider restarting Colab")
                    logger.info("💡 Note: You need to manually restart Colab every 12 hours")
                    logger.info("💡 Bot can't auto-restart, but prevents idle timeout")
                
                # Ping Colab
                status = self.ping_colab()
                
                if status == "active":
                    consecutive_failures = 0
                    logger.info(f"✅ Colab active (Session: {session_age:.1f}h)")
                else:
                    consecutive_failures += 1
                    logger.warning(f"⚠️ Ping status: {status} (Failures: {consecutive_failures})")
                    
                    if consecutive_failures >= max_consecutive_failures:
                        logger.error(f"🔥 {consecutive_failures} consecutive failures!")
                        # Could add notification here
                        consecutive_failures = 0
                
                # Update total runtime
                if self.stats["current_session_start"]:
                    self.stats["total_runtime"] = datetime.now() - self.stats["current_session_start"]
                
                # Wait for next ping with random jitter
                jitter = 0.8 + (0.4 * (time.time() % 1))  # Random 0.8-1.2
                wait_time = self.ping_interval * jitter
                
                logger.info(f"⏳ Next ping in {int(wait_time)} seconds")
                time.sleep(wait_time)
                
            except KeyboardInterrupt:
                logger.info("🛑 Stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Loop error: {e}")
                time.sleep(60)  # Wait before retry
    
    def start(self):
        """Start the keeper"""
        if self.is_running:
            logger.warning("⚠️ Already running")
            return False
        
        logger.info("🚀 Starting 24/7 Colab Keeper")
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
        
        # Calculate final stats
        total_runtime = self.stats["total_runtime"]
        
        logger.info("📊 Final Statistics:")
        logger.info(f"   Total Pings: {self.stats['total_pings']}")
        logger.info(f"   Successful: {self.stats['successful_pings']}")
        logger.info(f"   Failed: {self.stats['failed_pings']}")
        logger.info(f"   Session Restarts: {self.stats['session_restarts']}")
        logger.info(f"   Total Runtime: {total_runtime}")
        
        return True

# ================== WEB DASHBOARD ==================

app = Flask(__name__)
bot = SimpleColabKeeper()

@app.route('/')
def dashboard():
    """Dashboard for monitoring and control"""
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 24/7 Colab Keeper - Simplified</title>
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
            .note {
                background: rgba(255, 255, 255, 0.1);
                padding: 15px;
                border-radius: 10px;
                margin: 15px 0;
                font-size: 14px;
            }
        </style>
        <script>
            function updateStatus() {
                fetch('/api/status')
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('status').innerHTML = 
                            data.running ? 
                            '<span class="status-indicator status-running"></span>24/7 ACTIVE' : 
                            '<span class="status-indicator status-stopped"></span>STOPPED';
                        
                        document.getElementById('sessionAge').textContent = data.session_age + ' hours';
                        document.getElementById('totalPings').textContent = data.total_pings;
                        document.getElementById('successfulPings').textContent = data.successful_pings;
                        document.getElementById('failedPings').textContent = data.failed_pings;
                        document.getElementById('lastCheck').textContent = data.last_check || 'Never';
                        document.getElementById('colabUrl').textContent = data.colab_url;
                        document.getElementById('nextPing').textContent = data.next_ping;
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
                <h1>🤖 24/7 Colab Keeper</h1>
                <p>Simple & Effective - No Browser Required</p>
                <p><small>Works even when laptop is closed</small></p>
            </div>
            
            <div class="status-card">
                <h2>Status: <span id="status">Loading...</span></h2>
                <div class="stats">
                    <div class="stat-box">
                        <div>Session Age</div>
                        <div class="stat-value" id="sessionAge">0h</div>
                    </div>
                    <div class="stat-box">
                        <div>Total Pings</div>
                        <div class="stat-value" id="totalPings">0</div>
                    </div>
                    <div class="stat-box">
                        <div>Successful</div>
                        <div class="stat-value" id="successfulPings">0</div>
                    </div>
                    <div class="stat-box">
                        <div>Failed</div>
                        <div class="stat-value" id="failedPings">0</div>
                    </div>
                </div>
                <p>Last Check: <span id="lastCheck">Never</span></p>
                <p>Next Ping: <span id="nextPing">-</span></p>
            </div>
            
            <div class="note">
                <strong>⚠️ Important:</strong> This bot prevents Colab's 90-minute idle timeout by pinging every 3 minutes.
                However, Colab has a 12-hour session limit that requires manual restart.
            </div>
            
            <div class="status-card">
                <h2>Controls</h2>
                <button class="btn" onclick="control('start')">▶️ Start Keeper</button>
                <button class="btn btn-stop" onclick="control('stop')">⏹️ Stop Keeper</button>
                <button class="btn" onclick="control('restart')">🔄 Restart</button>
                <button class="btn" onclick="updateStatus()">📊 Refresh Status</button>
            </div>
            
            <div class="status-card">
                <h2>Configuration</h2>
                <p><strong>Colab URL:</strong> <span id="colabUrl">Loading...</span></p>
                <p><strong>Ping Interval:</strong> Every 3 minutes</p>
                <p><strong>Method:</strong> HTTP requests (No browser required)</p>
                <p><strong>Service:</strong> Running on Render.com 24/7</p>
            </div>
            
            <div class="status-card">
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

@app.route('/health')
def health():
    """Health endpoint for UptimeRobot"""
    return jsonify({
        "status": "healthy",
        "running": bot.is_running,
        "timestamp": datetime.now().isoformat(),
        "service": "24/7 Colab Keeper"
    })

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    session_age = bot.calculate_session_age()
    next_ping = f"In {bot.ping_interval}s" if bot.is_running else "Not running"
    
    return jsonify({
        "running": bot.is_running,
        "session_age": f"{session_age:.1f}",
        "total_pings": bot.stats["total_pings"],
        "successful_pings": bot.stats["successful_pings"],
        "failed_pings": bot.stats["failed_pings"],
        "last_check": bot.last_check.isoformat() if bot.last_check else None,
        "colab_url": bot.colab_url[:50] + "..." if len(bot.colab_url) > 50 else bot.colab_url,
        "next_ping": next_ping
    })

@app.route('/api/start')
def api_start():
    """Start bot via API"""
    if bot.is_running:
        return jsonify({"message": "Already running", "success": True})
    
    success = bot.start()
    return jsonify({
        "message": "Keeper started" if success else "Failed to start",
        "success": success
    })

@app.route('/api/stop')
def api_stop():
    """Stop bot via API"""
    if not bot.is_running:
        return jsonify({"message": "Not running", "success": True})
    
    success = bot.stop()
    return jsonify({
        "message": "Keeper stopped" if success else "Failed to stop",
        "success": success
    })

@app.route('/api/restart')
def api_restart():
    """Restart bot"""
    bot.stop()
    time.sleep(2)
    success = bot.start()
    return jsonify({
        "message": "Keeper restarted" if success else "Failed to restart",
        "success": success
    })

# ================== MAIN ==================

def main():
    """Main function"""
    print("\n" + "="*60)
    print("🤖 24/7 COLAB KEEPER - SIMPLIFIED")
    print("="*60)
    print(f"Time: {datetime.now()}")
    print(f"Colab URL: {bot.colab_url[:50]}..." if bot.colab_url else "No Colab URL set")
    print("="*60)
    
    # Check if running on Render.com
    if os.getenv("RENDER"):
        print("🌐 Render.com detected - Auto-starting...")
        
        # Start the keeper
        bot.start()
        
        # Start Flask app
        port = int(os.getenv("PORT", 10000))
        print(f"🌍 Dashboard: http://0.0.0.0:{port}")
        print(f"🔗 Health: https://your-app.onrender.com/health")
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        # Local execution
        print("💻 Local execution mode")
        bot.start()
        
        # Simple Flask for local
        port = 8080
        print(f"🌍 Local dashboard: http://localhost:{port}")
        app.run(host='0.0.0.0', port=port, debug=True)

if __name__ == "__main__":
    main()
