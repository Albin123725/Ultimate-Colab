#!/usr/bin/env python3
"""
🔥 24/7 COLAB AUTOMATION BOT
✅ Auto-restarts Colab when session dies (12-hour limit)
✅ Auto-login with saved cookies
✅ Auto-run cells after restart
✅ Email/Telegram notifications
✅ Smart session management
✅ Works when laptop is closed
"""

import os
import time
import json
import logging
import threading
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from flask import Flask, jsonify, render_template_string
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UltimateColabBot:
    def __init__(self):
        self.is_running = False
        self.driver = None
        self.session_start_time = None
        self.current_session_age = 0
        
        # Configuration
        self.colab_url = os.getenv("COLAB_URL", "")
        self.google_email = os.getenv("GOOGLE_EMAIL", "")
        self.google_password = os.getenv("GOOGLE_PASSWORD", "")  # Use App Password!
        
        # Notification settings
        self.telegram_token = os.getenv("TELEGRAM_TOKEN", "")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_email = os.getenv("SMTP_EMAIL", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.notify_email = os.getenv("NOTIFY_EMAIL", "")
        
        # Session management
        self.session_max_hours = 11.5  # Restart at 11.5 hours to be safe
        self.check_interval = 180  # 3 minutes
        self.restart_attempts = 0
        self.max_restart_attempts = 5
        
        # Statistics
        self.stats = {
            "total_sessions": 0,
            "total_runtime": timedelta(0),
            "successful_restarts": 0,
            "failed_restarts": 0,
            "last_restart": None,
            "current_session_start": None
        }
        
        if not self.colab_url:
            logger.error("❌ COLAB_URL not set!")
        
        logger.info("🤖 24/7 Colab Bot Initialized")
    
    # ================= NOTIFICATION SYSTEM =================
    
    def send_notification(self, title, message, urgent=False):
        """Send notification via all configured channels"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"[{timestamp}] {title}\n{message}"
        
        # Telegram
        if self.telegram_token and self.telegram_chat_id:
            try:
                url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
                payload = {
                    "chat_id": self.telegram_chat_id,
                    "text": full_message,
                    "parse_mode": "HTML"
                }
                requests.post(url, json=payload, timeout=10)
                logger.info("📱 Telegram notification sent")
            except Exception as e:
                logger.error(f"Telegram error: {e}")
        
        # Email
        if self.smtp_email and self.smtp_password and self.notify_email:
            try:
                msg = MIMEText(full_message)
                msg['Subject'] = f"{'🚨' if urgent else '📢'} {title}"
                msg['From'] = self.smtp_email
                msg['To'] = self.notify_email
                
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_email, self.smtp_password)
                    server.send_message(msg)
                logger.info("📧 Email notification sent")
            except Exception as e:
                logger.error(f"Email error: {e}")
        
        # Always log
        if urgent:
            logger.warning(f"🚨 {full_message}")
        else:
            logger.info(f"📢 {full_message}")
    
    # ================= BROWSER MANAGEMENT =================
    
    def setup_browser(self):
        """Setup headless browser for automation"""
        try:
            options = webdriver.ChromeOptions()
            
            # Headless mode (works without display)
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-blink-features=AutomationControlled")
            
            # User agent
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            # Try to find Chrome binary in common locations
            chrome_paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/chromium-browser",
                "/usr/local/bin/chromedriver",
                "/opt/google/chrome/chrome"
            ]
            
            for path in chrome_paths:
                if os.path.exists(path):
                    options.binary_location = path
                    break
            
            # Create driver
            self.driver = webdriver.Chrome(options=options)
            
            # Anti-detection
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("✅ Browser setup complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Browser setup failed: {e}")
            return False
    
    def save_cookies(self):
        """Save login cookies"""
        try:
            if self.driver:
                cookies = self.driver.get_cookies()
                with open("google_cookies.json", "w") as f:
                    json.dump(cookies, f)
                logger.info("💾 Cookies saved")
                return True
        except:
            pass
        return False
    
    def load_cookies(self):
        """Load saved cookies"""
        try:
            with open("google_cookies.json", "r") as f:
                cookies = json.load(f)
            
            if self.driver:
                self.driver.delete_all_cookies()
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except:
                        pass
                logger.info("📂 Cookies loaded")
                return True
        except:
            pass
        return False
    
    # ================= COLAB AUTOMATION =================
    
    def google_login(self):
        """Login to Google account"""
        logger.info("🔐 Attempting Google login...")
        
        try:
            # Go to accounts page
            self.driver.get("https://accounts.google.com")
            time.sleep(3)
            
            # Try cookies first
            if self.load_cookies():
                self.driver.refresh()
                time.sleep(3)
                
                # Check if login successful
                if "myaccount.google.com" in self.driver.current_url:
                    logger.info("✅ Logged in via cookies")
                    return True
            
            # Manual login
            if not self.google_email or not self.google_password:
                logger.error("❌ No login credentials")
                return False
            
            # Enter email
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "identifierId"))
            )
            email_field.send_keys(self.google_email)
            email_field.send_keys(Keys.RETURN)
            time.sleep(3)
            
            # Enter password
            password_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "Passwd"))
            )
            password_field.send_keys(self.google_password)
            password_field.send_keys(Keys.RETURN)
            time.sleep(5)
            
            # Save cookies
            self.save_cookies()
            
            logger.info("✅ Manual login successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Login failed: {e}")
            return False
    
    def restart_colab_session(self):
        """Completely restart Colab session after 12-hour limit"""
        logger.info("🔄 RESTARTING COLAB SESSION...")
        
        self.send_notification(
            "Colab Session Restarting",
            f"Session ran for {self.current_session_age:.1f} hours. Starting new session...",
            urgent=True
        )
        
        try:
            # Close old session if exists
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
            
            # Setup new browser
            if not self.setup_browser():
                return False
            
            # Login to Google
            if not self.google_login():
                logger.error("❌ Login failed, cannot restart")
                return False
            
            # Navigate to Colab
            self.driver.get(self.colab_url)
            time.sleep(5)
            
            # Click "Connect" if available
            self.click_connect_button()
            time.sleep(10)  # Wait for runtime
            
            # Run all cells
            self.run_all_cells()
            time.sleep(5)
            
            # Update statistics
            self.stats["total_sessions"] += 1
            self.stats["successful_restarts"] += 1
            self.stats["last_restart"] = datetime.now()
            self.stats["current_session_start"] = datetime.now()
            
            self.restart_attempts = 0
            self.session_start_time = datetime.now()
            
            self.send_notification(
                "✅ Colab Session Restarted",
                f"New session started successfully!\n"
                f"Total sessions: {self.stats['total_sessions']}\n"
                f"URL: {self.colab_url}",
                urgent=False
            )
            
            logger.info("✅ Colab session restarted successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Session restart failed: {e}")
            self.stats["failed_restarts"] += 1
            self.restart_attempts += 1
            
            self.send_notification(
                "❌ Colab Restart FAILED",
                f"Attempt {self.restart_attempts} failed: {str(e)[:100]}\n"
                f"Will retry in 10 minutes...",
                urgent=True
            )
            
            return False
    
    def click_connect_button(self):
        """Click Connect/Runtime button"""
        try:
            # Try different button selectors
            selectors = [
                "//*[contains(text(), 'Connect')]",
                "//*[contains(text(), 'RECONNECT')]",
                "//colab-connect-button",
                "//paper-button[contains(., 'Connect')]",
                "//button[contains(., 'Connect')]"
            ]
            
            for selector in selectors:
                try:
                    buttons = self.driver.find_elements(By.XPATH, selector)
                    for button in buttons:
                        if button.is_displayed():
                            button.click()
                            logger.info(f"✅ Clicked: {selector}")
                            return True
                except:
                    continue
            
            # If no connect button, maybe runtime is already connected
            return True
            
        except Exception as e:
            logger.error(f"❌ Connect click failed: {e}")
            return False
    
    def run_all_cells(self):
        """Run all cells in notebook"""
        try:
            # Press Ctrl+F9 (run all)
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(self.driver)
            actions.key_down(Keys.CONTROL).send_keys(Keys.F9).key_up(Keys.CONTROL).perform()
            logger.info("✅ Sent Ctrl+F9 to run all cells")
            return True
        except Exception as e:
            logger.error(f"❌ Run cells failed: {e}")
            return False
    
    def check_colab_status(self):
        """Check if Colab is running properly"""
        try:
            page_source = self.driver.page_source.lower()
            
            # Check for disconnection
            if "disconnected" in page_source or "reconnect" in page_source:
                return "disconnected"
            
            # Check for login required
            if "sign in" in page_source or "accounts.google.com" in self.driver.current_url:
                return "login_required"
            
            # Check for running cells
            if "stop button" in page_source or "executing" in page_source:
                return "running"
            
            return "idle"
            
        except Exception as e:
            logger.error(f"❌ Status check failed: {e}")
            return "error"
    
    def reset_idle_timer(self):
        """Reset Colab idle timer"""
        try:
            # Simple refresh usually works
            self.driver.refresh()
            time.sleep(3)
            logger.info("🔄 Refreshed page to reset idle timer")
            return True
        except:
            return False
    
    # ================= MAIN LOOP =================
    
    def monitor_loop(self):
        """Main 24/7 monitoring loop"""
        logger.info("🚀 Starting 24/7 Colab monitoring...")
        
        # Initial setup
        if not self.setup_browser():
            logger.error("❌ Initial browser setup failed")
            return
        
        if not self.google_login():
            logger.error("❌ Initial login failed")
            return
        
        # Navigate to Colab
        self.driver.get(self.colab_url)
        time.sleep(5)
        
        # Start first session
        self.session_start_time = datetime.now()
        self.stats["current_session_start"] = datetime.now()
        self.stats["total_sessions"] = 1
        
        self.send_notification(
            "🚀 24/7 Colab Bot Started",
            f"Bot is now monitoring your Colab 24/7!\n"
            f"URL: {self.colab_url}\n"
            f"Session started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            urgent=False
        )
        
        consecutive_errors = 0
        
        while self.is_running:
            try:
                # Calculate session age
                if self.session_start_time:
                    self.current_session_age = (datetime.now() - self.session_start_time).total_seconds() / 3600
                
                # Check 1: Session too old (near 12-hour limit)
                if self.current_session_age > self.session_max_hours:
                    logger.warning(f"⚠️ Session age: {self.current_session_age:.1f}h - Restarting...")
                    
                    if not self.restart_colab_session():
                        time.sleep(600)  # Wait 10 minutes before retry
                        continue
                
                # Check 2: Current Colab status
                status = self.check_colab_status()
                
                if status == "disconnected":
                    logger.warning("⚠️ Colab disconnected, reconnecting...")
                    self.click_connect_button()
                    time.sleep(10)
                    
                elif status == "login_required":
                    logger.warning("⚠️ Login required, re-logging...")
                    self.google_login()
                    time.sleep(5)
                    
                elif status == "idle":
                    logger.info("🔄 Resetting idle timer...")
                    self.reset_idle_timer()
                
                elif status == "running":
                    logger.info("✅ Colab running normally")
                
                # Reset error counter on success
                consecutive_errors = 0
                
                # Update total runtime
                if self.stats["current_session_start"]:
                    self.stats["total_runtime"] = datetime.now() - self.stats["current_session_start"]
                
                # Wait for next check
                time.sleep(self.check_interval)
                
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"❌ Loop error #{consecutive_errors}: {e}")
                
                if consecutive_errors >= 3:
                    self.send_notification(
                        "🚨 Colab Bot Critical Error",
                        f"3 consecutive errors:\n{str(e)[:200]}",
                        urgent=True
                    )
                    consecutive_errors = 0
                
                # Try to recover browser
                try:
                    if self.driver:
                        self.driver.quit()
                except:
                    pass
                
                time.sleep(30)  # Wait before retry
                
                # Re-setup
                self.setup_browser()
                self.google_login()
    
    def start(self):
        """Start the 24/7 bot"""
        if self.is_running:
            logger.warning("⚠️ Bot already running")
            return False
        
        self.is_running = True
        
        # Start in background thread
        thread = threading.Thread(target=self.monitor_loop, daemon=True)
        thread.start()
        
        logger.info("✅ 24/7 Colab Bot started")
        return True
    
    def stop(self):
        """Stop the bot"""
        logger.info("🛑 Stopping 24/7 Colab Bot...")
        self.is_running = False
        
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        
        # Send final stats
        total_runtime = self.stats["total_runtime"]
        
        self.send_notification(
            "🛑 Colab Bot Stopped",
            f"Final Statistics:\n"
            f"Total Sessions: {self.stats['total_sessions']}\n"
            f"Total Runtime: {total_runtime}\n"
            f"Successful Restarts: {self.stats['successful_restarts']}\n"
            f"Failed Restarts: {self.stats['failed_restarts']}",
            urgent=False
        )
        
        logger.info("📊 Final stats logged")
        return True

# ================= FLASK WEB DASHBOARD =================

app = Flask(__name__)
bot = UltimateColabBot()

@app.route('/')
def dashboard():
    """Web dashboard"""
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>24/7 Colab Bot Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #0f172a; color: white; }
            .container { max-width: 1000px; margin: 0 auto; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 15px; margin-bottom: 30px; }
            .card { background: #1e293b; padding: 25px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); }
            .btn { background: #10b981; color: white; border: none; padding: 15px 30px; border-radius: 8px; cursor: pointer; margin: 10px; font-size: 16px; }
            .btn:hover { opacity: 0.9; }
            .btn-stop { background: #ef4444; }
            .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
            .stat-box { background: #334155; padding: 20px; border-radius: 10px; text-align: center; }
            .stat-value { font-size: 2em; font-weight: bold; margin: 10px 0; }
            .status-indicator { display: inline-block; width: 15px; height: 15px; border-radius: 50%; margin-right: 10px; }
            .status-online { background: #10b981; animation: pulse 2s infinite; }
            .status-offline { background: #ef4444; }
            @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
        </style>
        <script>
            function updateStatus() {
                fetch('/api/status')
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('status').innerHTML = 
                            data.running ? 
                            '<span class="status-indicator status-online"></span>24/7 ACTIVE' : 
                            '<span class="status-indicator status-offline"></span>STOPPED';
                        
                        document.getElementById('sessionAge').textContent = data.session_age + ' hours';
                        document.getElementById('totalSessions').textContent = data.total_sessions;
                        document.getElementById('totalRuntime').textContent = data.total_runtime;
                        document.getElementById('successfulRestarts').textContent = data.successful_restarts;
                        document.getElementById('failedRestarts').textContent = data.failed_restarts;
                        document.getElementById('nextRestart').textContent = data.next_restart;
                        document.getElementById('colabStatus').textContent = data.colab_status;
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
            
            function forceRestart() {
                if(confirm('Force restart Colab session now?')) {
                    fetch('/api/force-restart')
                        .then(r => r.json())
                        .then(data => {
                            alert(data.message);
                            updateStatus();
                        });
                }
            }
            
            // Auto-update every 5 seconds
            setInterval(updateStatus, 5000);
            window.onload = updateStatus;
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 24/7 Colab Automation Bot</h1>
                <p>Keeps your Colab running even when your laptop is closed</p>
            </div>
            
            <div class="card">
                <h2>Bot Status: <span id="status">Loading...</span></h2>
                <div class="stats-grid">
                    <div class="stat-box">
                        <div>Current Session Age</div>
                        <div class="stat-value" id="sessionAge">0h</div>
                    </div>
                    <div class="stat-box">
                        <div>Total Sessions</div>
                        <div class="stat-value" id="totalSessions">0</div>
                    </div>
                    <div class="stat-box">
                        <div>Total Runtime</div>
                        <div class="stat-value" id="totalRuntime">0:00:00</div>
                    </div>
                    <div class="stat-box">
                        <div>Successful Restarts</div>
                        <div class="stat-value" id="successfulRestarts">0</div>
                    </div>
                </div>
                <p>Colab Status: <span id="colabStatus">Checking...</span></p>
                <p>Next Auto-Restart: <span id="nextRestart">Calculating...</span></p>
            </div>
            
            <div class="card">
                <h2>Controls</h2>
                <button class="btn" onclick="control('start')">🚀 Start 24/7 Bot</button>
                <button class="btn btn-stop" onclick="control('stop')">⏹️ Stop Bot</button>
                <button class="btn" onclick="forceRestart()">🔄 Force Restart Now</button>
                <button class="btn" onclick="control('status')">📊 Refresh Status</button>
            </div>
            
            <div class="card">
                <h2>How It Works</h2>
                <p>✅ Automatically restarts Colab every 11.5 hours (before 12h limit)</p>
                <p>✅ Auto-login with saved cookies</p>
                <p>✅ Auto-runs all cells after restart</p>
                <p>✅ Sends Telegram/Email notifications</p>
                <p>✅ Works 24/7 even when laptop is closed</p>
            </div>
            
            <div class="card">
                <h2>Quick Links</h2>
                <a href="/health" target="_blank"><button class="btn">Health Check</button></a>
                <a href="/api/status" target="_blank"><button class="btn">API Status</button></a>
                <a href="''' + bot.colab_url + '''" target="_blank"><button class="btn">Open Colab</button></a>
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
        "bot_running": bot.is_running,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    session_age = bot.current_session_age if hasattr(bot, 'current_session_age') else 0
    next_restart = max(0, bot.session_max_hours - session_age) if bot.is_running else 0
    
    return jsonify({
        "running": bot.is_running,
        "session_age": f"{session_age:.1f}",
        "total_sessions": bot.stats["total_sessions"],
        "total_runtime": str(bot.stats["total_runtime"]).split('.')[0],
        "successful_restarts": bot.stats["successful_restarts"],
        "failed_restarts": bot.stats["failed_restarts"],
        "next_restart": f"In {next_restart:.1f} hours",
        "colab_status": "Active" if bot.is_running else "Inactive"
    })

@app.route('/api/start')
def api_start():
    """Start bot via API"""
    if bot.is_running:
        return jsonify({"message": "Bot already running"})
    
    success = bot.start()
    return jsonify({
        "message": "24/7 Bot started" if success else "Failed to start",
        "success": success
    })

@app.route('/api/stop')
def api_stop():
    """Stop bot via API"""
    if not bot.is_running:
        return jsonify({"message": "Bot not running"})
    
    success = bot.stop()
    return jsonify({
        "message": "Bot stopped" if success else "Failed to stop",
        "success": success
    })

@app.route('/api/force-restart')
def force_restart():
    """Force restart Colab session"""
    if not bot.is_running:
        return jsonify({"message": "Start bot first", "success": False})
    
    success = bot.restart_colab_session()
    return jsonify({
        "message": "Colab restarted" if success else "Restart failed",
        "success": success
    })

# ================= MAIN EXECUTION =================

def main():
    """Main function"""
    print("\n" + "="*60)
    print("🤖 24/7 COLAB AUTOMATION BOT")
    print("="*60)
    print(f"Colab URL: {bot.colab_url[:50]}...")
    print(f"Bot Mode: 24/7 Auto-Restart")
    print("="*60)
    
    # Check environment
    if not bot.colab_url:
        print("❌ ERROR: Set COLAB_URL environment variable")
        print("💡 On Render.com: Environment → Add COLAB_URL")
        return
    
    # Start bot automatically on Render.com
    if os.getenv("RENDER"):
        print("🌐 Render.com detected - Starting bot automatically...")
        bot.start()
        
        # Start Flask app
        port = int(os.getenv("PORT", 10000))
        print(f"🌍 Dashboard: http://0.0.0.0:{port}")
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        # Local execution
        print("💻 Local execution - Starting bot...")
        bot.start()
        
        # Simple web interface
        @app.route('/local')
        def local_dashboard():
            return "<h1>24/7 Colab Bot Running</h1><p>Check console for logs</p>"
        
        app.run(host='0.0.0.0', port=8080, debug=True)

if __name__ == "__main__":
    main()
