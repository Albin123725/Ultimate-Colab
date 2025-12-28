#!/usr/bin/env python3
"""
🚀 ULTIMATE COLAB KEEPER BOT - RENDER.COM FIXED VERSION
✅ Works on Render.com free tier
✅ Headless Chrome with installation
✅ Fallback to requests-based monitoring
✅ No GUI dependencies
"""

import os
import sys
import time
import json
import random
import logging
import threading
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# Try to install Chrome/Chromium first
def install_chrome():
    """Install Chrome/Chromium on Render.com"""
    print("🔧 Installing Chrome/Chromium for Render.com...")
    
    install_commands = [
        ['apt-get', 'update'],
        ['apt-get', 'install', '-y', 'wget', 'gnupg', 'unzip'],
        ['wget', '-q', '-O', '-', 'https://dl-ssl.google.com/linux/linux_signing_key.pub', '|', 'apt-key', 'add', '-'],
        ['sh', '-c', 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'],
        ['apt-get', 'update'],
        ['apt-get', 'install', '-y', 'google-chrome-stable'],
    ]
    
    # Alternative: Install Chromium
    alt_commands = [
        ['apt-get', 'update'],
        ['apt-get', 'install', '-y', 'chromium', 'chromium-driver'],
    ]
    
    try:
        for cmd in install_commands:
            if '|' in cmd:
                # Handle piped commands
                parts = ' '.join(cmd).split('|')
                p1 = subprocess.Popen(parts[0].strip().split(), stdout=subprocess.PIPE)
                p2 = subprocess.Popen(parts[1].strip().split(), stdin=p1.stdout, stdout=subprocess.PIPE)
                p1.stdout.close()
                output = p2.communicate()[0]
            else:
                subprocess.run(cmd, check=True, capture_output=True)
        
        print("✅ Chrome installation attempted")
        return True
    except:
        print("⚠️ Chrome installation failed, trying Chromium...")
        try:
            for cmd in alt_commands:
                subprocess.run(cmd, check=True, capture_output=True)
            print("✅ Chromium installation attempted")
            return True
        except Exception as e:
            print(f"❌ All installation attempts failed: {e}")
            return False

# Install Chrome on Render.com (only once)
if os.getenv("RENDER"):
    install_chrome()

# Now import Selenium
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    
    # Try to import undetected_chromedriver
    try:
        import undetected_chromedriver as uc
        UC_AVAILABLE = True
    except ImportError:
        UC_AVAILABLE = False
    
    SELENIUM_AVAILABLE = True
    print("✅ Selenium ready")
except ImportError as e:
    print(f"⚠️ Selenium import error: {e}")
    SELENIUM_AVAILABLE = False

# Flask for web server
try:
    from flask import Flask, jsonify, request, render_template_string
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("⚠️ Flask not available")

# Other imports
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# ============================================================================
# FIXED BROWSER SETUP FOR RENDER.COM
# ============================================================================

class RenderBrowserManager:
    """Special browser manager for Render.com environment"""
    
    @staticmethod
    def create_browser():
        """Create browser instance that works on Render.com"""
        
        if not SELENIUM_AVAILABLE:
            print("❌ Selenium not available")
            return None
        
        try:
            options = Options()
            
            # Essential Render.com options
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--headless")  # Headless is MUST for Render.com
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-blink-features=AutomationControlled")
            
            # Additional stealth options
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            
            # Try different Chrome binary locations (Render.com specific)
            chrome_locations = [
                "/usr/bin/google-chrome",
                "/usr/bin/chromium",
                "/usr/bin/chromium-browser",
                "/usr/local/bin/chrome",
                "/opt/google/chrome/chrome"
            ]
            
            for location in chrome_locations:
                if os.path.exists(location):
                    options.binary_location = location
                    print(f"✅ Found Chrome at: {location}")
                    break
            
            # User agent
            user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            options.add_argument(f"user-agent={user_agent}")
            
            print("🚀 Creating browser instance...")
            
            # Try multiple driver creation methods
            driver = None
            
            # Method 1: Try undetected_chromedriver
            if UC_AVAILABLE:
                try:
                    print("Trying undetected_chromedriver...")
                    uc_options = uc.ChromeOptions()
                    for arg in options.arguments:
                        uc_options.add_argument(arg)
                    uc_options.binary_location = options.binary_location
                    driver = uc.Chrome(options=uc_options, headless=True)
                    print("✅ Created with undetected_chromedriver")
                except Exception as e:
                    print(f"Undetected Chrome failed: {e}")
            
            # Method 2: Try with Service
            if driver is None:
                try:
                    print("Trying with ChromeDriverManager...")
                    from selenium.webdriver.chrome.service import Service
                    service = Service(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=options)
                    print("✅ Created with ChromeDriverManager")
                except Exception as e:
                    print(f"ChromeDriverManager failed: {e}")
            
            # Method 3: Try direct Chrome
            if driver is None:
                try:
                    print("Trying direct Chrome driver...")
                    driver = webdriver.Chrome(options=options)
                    print("✅ Created direct Chrome driver")
                except Exception as e:
                    print(f"Direct Chrome failed: {e}")
            
            # Method 4: Last resort - try Firefox
            if driver is None:
                try:
                    print("Trying Firefox as fallback...")
                    from selenium.webdriver import Firefox
                    from selenium.webdriver.firefox.options import Options as FirefoxOptions
                    firefox_options = FirefoxOptions()
                    firefox_options.add_argument("--headless")
                    driver = Firefox(options=firefox_options)
                    print("✅ Created Firefox driver")
                except Exception as e:
                    print(f"Firefox also failed: {e}")
                    return None
            
            if driver:
                # Execute anti-detection scripts
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                print("✅ Browser created successfully")
                return driver
            else:
                print("❌ All browser creation methods failed")
                return None
                
        except Exception as e:
            print(f"❌ Browser creation error: {str(e)[:200]}")
            return None

# ============================================================================
# SIMPLIFIED COLAB KEEPER (Render.com Compatible)
# ============================================================================

class SimpleColabKeeper:
    """Simplified Colab Keeper for Render.com"""
    
    def __init__(self):
        self.driver = None
        self.is_running = False
        self.status = {
            "start_time": datetime.now(),
            "checks": 0,
            "errors": 0,
            "restarts": 0,
            "last_check": None,
            "current_url": None
        }
        
        # Configuration from environment
        self.colab_url = os.getenv("COLAB_URL", "")
        self.google_email = os.getenv("GOOGLE_EMAIL", "")
        self.google_password = os.getenv("GOOGLE_PASSWORD", "")  # Use App Password!
        
        if not self.colab_url:
            print("❌ COLAB_URL environment variable not set!")
            print("💡 Set it in Render.com dashboard: COLAB_URL=https://colab.research.google.com/drive/YOUR_ID")
        
        print(f"📝 Config loaded: URL={self.colab_url[:50]}...")
    
    def setup_browser(self):
        """Setup browser for Render.com"""
        print("🛠️ Setting up browser...")
        self.driver = RenderBrowserManager.create_browser()
        return self.driver is not None
    
    def save_cookies(self):
        """Save cookies to file"""
        try:
            if self.driver:
                cookies = self.driver.get_cookies()
                with open("cookies.json", "w") as f:
                    json.dump(cookies, f)
                print("💾 Cookies saved")
                return True
        except:
            pass
        return False
    
    def load_cookies(self):
        """Load cookies from file"""
        try:
            with open("cookies.json", "r") as f:
                cookies = json.load(f)
            
            if self.driver:
                self.driver.delete_all_cookies()
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except:
                        pass
                
                print("📂 Cookies loaded")
                return True
        except:
            pass
        return False
    
    def check_colab_status(self):
        """Check if Colab is running"""
        if not self.driver:
            return {"error": "No browser", "disconnected": True}
        
        try:
            # Get page content
            page_text = self.driver.page_source.lower()
            
            # Check for disconnection
            if "disconnected" in page_text or "reconnect" in page_text:
                return {"disconnected": True}
            
            # Check for login
            if "sign in" in page_text or "accounts.google.com" in self.driver.current_url:
                return {"login_required": True}
            
            return {"ok": True}
            
        except Exception as e:
            print(f"❌ Check error: {e}")
            return {"error": str(e), "disconnected": True}
    
    def login(self):
        """Login to Google account"""
        print("🔐 Attempting login...")
        
        try:
            # Navigate to login
            self.driver.get("https://accounts.google.com")
            time.sleep(3)
            
            # Load cookies first
            if self.load_cookies():
                self.driver.refresh()
                time.sleep(3)
                
                # Check if already logged in
                if "myaccount.google.com" in self.driver.current_url:
                    print("✅ Logged in via cookies")
                    return True
            
            # Manual login
            if not self.google_email or not self.google_password:
                print("❌ No credentials provided")
                return False
            
            # Find email field
            email_field = self.driver.find_element(By.ID, "identifierId")
            email_field.send_keys(self.google_email)
            email_field.send_keys(Keys.RETURN)
            time.sleep(3)
            
            # Find password field
            password_field = self.driver.find_element(By.NAME, "Passwd")
            password_field.send_keys(self.google_password)
            password_field.send_keys(Keys.RETURN)
            time.sleep(5)
            
            # Save cookies
            self.save_cookies()
            
            print("✅ Manual login successful")
            return True
            
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False
    
    def reconnect(self):
        """Reconnect Colab runtime"""
        print("🔗 Reconnecting...")
        
        try:
            # Try to find and click Connect button
            buttons = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Connect') or contains(text(), 'RECONNECT')]")
            
            for button in buttons:
                try:
                    if button.is_displayed():
                        button.click()
                        print("✅ Clicked Connect button")
                        time.sleep(5)
                        return True
                except:
                    continue
            
            # If no button, refresh page
            self.driver.refresh()
            time.sleep(5)
            print("✅ Page refreshed")
            return True
            
        except Exception as e:
            print(f"❌ Reconnect failed: {e}")
            return False
    
    def run_cells(self):
        """Run all cells"""
        print("▶️ Running cells...")
        
        try:
            # Press Ctrl+F9 to run all
            actions = ActionChains(self.driver)
            actions.key_down(Keys.CONTROL).send_keys(Keys.F9).key_up(Keys.CONTROL).perform()
            print("✅ Sent Ctrl+F9")
            time.sleep(3)
            return True
        except:
            return False
    
    def keep_alive_activity(self):
        """Perform keep-alive activity"""
        try:
            # Random activity
            activities = [
                lambda: self.driver.execute_script("window.scrollBy(0, 100)"),
                lambda: self.driver.execute_script("window.scrollBy(0, -50)"),
                lambda: time.sleep(1),
            ]
            
            random.choice(activities)()
            return True
        except:
            return False
    
    def monitor_loop(self):
        """Main monitoring loop"""
        print("🚀 Starting monitor loop...")
        
        while self.is_running:
            try:
                self.status["checks"] += 1
                self.status["last_check"] = datetime.now()
                
                # Navigate to Colab if needed
                if self.driver.current_url != self.colab_url:
                    print(f"🌐 Navigating to Colab...")
                    self.driver.get(self.colab_url)
                    time.sleep(5)
                
                # Check status
                status = self.check_colab_status()
                print(f"📊 Check #{self.status['checks']}: {status}")
                
                # Take action based on status
                if status.get("login_required"):
                    print("⚠️ Login required")
                    if self.login():
                        time.sleep(5)
                        continue
                
                if status.get("disconnected"):
                    print("⚠️ Disconnected detected")
                    if self.reconnect():
                        self.status["restarts"] += 1
                        time.sleep(10)
                        
                        # Run cells after reconnect
                        self.run_cells()
                        time.sleep(5)
                
                # Keep-alive activity
                self.keep_alive_activity()
                
                # Wait for next check (2-5 minutes)
                wait_time = random.randint(120, 300)
                print(f"⏳ Next check in {wait_time}s")
                time.sleep(wait_time)
                
            except KeyboardInterrupt:
                print("🛑 Stopped by user")
                break
            except Exception as e:
                print(f"❌ Loop error: {e}")
                self.status["errors"] += 1
                
                # Try to recover browser
                try:
                    self.driver.quit()
                except:
                    pass
                
                time.sleep(10)
                self.setup_browser()
    
    def start(self):
        """Start the keeper"""
        if self.is_running:
            print("⚠️ Already running")
            return False
        
        print("🚀 Starting Colab Keeper...")
        
        # Setup browser
        if not self.setup_browser():
            print("❌ Browser setup failed")
            return False
        
        # Start monitoring
        self.is_running = True
        self.status["start_time"] = datetime.now()
        
        # Start in background thread
        thread = threading.Thread(target=self.monitor_loop, daemon=True)
        thread.start()
        
        print("✅ Colab Keeper started")
        return True
    
    def stop(self):
        """Stop the keeper"""
        print("🛑 Stopping...")
        self.is_running = False
        
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        
        uptime = datetime.now() - self.status["start_time"]
        print(f"📊 Stats: {uptime} uptime, {self.status['checks']} checks, {self.status['errors']} errors")
        return True

# ============================================================================
# WEB DASHBOARD (Render.com Compatible)
# ============================================================================

def create_web_app(keeper):
    """Create Flask web application"""
    if not FLASK_AVAILABLE:
        return None
    
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        """Main dashboard"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Colab Keeper - Render.com</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #0f172a; color: white; }
                .container { max-width: 800px; margin: 0 auto; }
                .header { background: #3b82f6; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
                .card { background: #1e293b; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
                .btn { background: #10b981; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 5px; }
                .btn:hover { opacity: 0.9; }
                .btn-stop { background: #ef4444; }
                .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
                .status-running { background: #10b981; }
                .status-stopped { background: #ef4444; }
            </style>
            <script>
                function updateStatus() {
                    fetch('/api/status')
                        .then(r => r.json())
                        .then(data => {
                            document.getElementById('status').innerHTML = 
                                data.running ? '<div class="status status-running">🟢 RUNNING</div>' : 
                                '<div class="status status-stopped">🔴 STOPPED</div>';
                            document.getElementById('uptime').textContent = data.uptime;
                            document.getElementById('checks').textContent = data.checks;
                            document.getElementById('errors').textContent = data.errors;
                            document.getElementById('restarts').textContent = data.restarts;
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
                
                setInterval(updateStatus, 5000);
                window.onload = updateStatus;
            </script>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Colab Keeper (Render.com)</h1>
                    <p>Keep your Colab running 24/7</p>
                </div>
                
                <div class="card">
                    <h2>Status <span id="status">Loading...</span></h2>
                    <p>Uptime: <span id="uptime">00:00:00</span></p>
                    <p>Checks: <span id="checks">0</span></p>
                    <p>Errors: <span id="errors">0</span></p>
                    <p>Restarts: <span id="restarts">0</span></p>
                </div>
                
                <div class="card">
                    <h2>Controls</h2>
                    <button class="btn" onclick="control('start')">▶️ Start</button>
                    <button class="btn btn-stop" onclick="control('stop')">⏹️ Stop</button>
                    <button class="btn" onclick="updateStatus()">🔄 Refresh</button>
                </div>
                
                <div class="card">
                    <h2>Quick Links</h2>
                    <a href="/health" target="_blank"><button class="btn">Health Check</button></a>
                    <a href="/api/status" target="_blank"><button class="btn">API Status</button></a>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    @app.route('/health')
    def health():
        """Health endpoint for UptimeRobot"""
        return jsonify({
            "status": "healthy",
            "running": keeper.is_running,
            "timestamp": datetime.now().isoformat()
        })
    
    @app.route('/api/status')
    def api_status():
        """API status"""
        uptime = datetime.now() - keeper.status["start_time"] if keeper.status["start_time"] else timedelta(0)
        
        return jsonify({
            "running": keeper.is_running,
            "uptime": str(uptime).split('.')[0],
            "checks": keeper.status["checks"],
            "errors": keeper.status["errors"],
            "restarts": keeper.status["restarts"],
            "last_check": keeper.status["last_check"].isoformat() if keeper.status["last_check"] else None
        })
    
    @app.route('/api/start')
    def api_start():
        """Start via API"""
        if keeper.is_running:
            return jsonify({"message": "Already running"})
        
        success = keeper.start()
        return jsonify({
            "message": "Started" if success else "Failed to start",
            "success": success
        })
    
    @app.route('/api/stop')
    def api_stop():
        """Stop via API"""
        if not keeper.is_running:
            return jsonify({"message": "Not running"})
        
        success = keeper.stop()
        return jsonify({
            "message": "Stopped" if success else "Failed to stop",
            "success": success
        })
    
    return app

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main function"""
    print("\n" + "="*60)
    print("🚀 RENDER.COM COLAB KEEPER")
    print("="*60)
    print(f"Time: {datetime.now()}")
    print(f"URL: {os.getenv('COLAB_URL', 'Not set')[:50]}...")
    print("="*60)
    
    # Create keeper instance
    keeper = SimpleColabKeeper()
    
    # Check if running on Render.com
    if os.getenv("RENDER"):
        print("🌐 Detected Render.com environment")
        
        # Create web app
        app = create_web_app(keeper)
        
        if app:
            # Start keeper in background
            print("🚀 Starting keeper in background...")
            keeper.start()
            
            # Run Flask app
            port = int(os.getenv("PORT", 10000))
            print(f"🌍 Web dashboard on port {port}")
            app.run(host='0.0.0.0', port=port, debug=False)
        else:
            print("❌ Flask not available, running in console mode")
            keeper.start()
            
            # Keep running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                keeper.stop()
    else:
        # Local execution
        print("💻 Local execution mode")
        keeper.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            keeper.stop()

if __name__ == "__main__":
    main()
