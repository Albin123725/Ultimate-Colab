#!/usr/bin/env python3
"""
🔥 24/7 COLAB BOT - COMPLETE AUTOMATION
✅ Creates NEW Colab sessions after termination
✅ Auto-uploads code from GitHub/Gist
✅ Auto-runs all cells
✅ Works when browser/laptop closed
✅ Full session lifecycle management
"""

import os
import time
import json
import logging
import threading
import subprocess
from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template_string
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CompleteColabAutomation:
    """Complete 24/7 Colab automation - handles everything"""
    
    def __init__(self):
        self.is_running = False
        self.driver = None
        self.session_start = None
        
        # Configuration
        self.colab_notebook_url = os.getenv("COLAB_URL", "")
        self.github_gist_url = os.getenv("GITHUB_GIST_URL", "")
        self.google_email = os.getenv("GOOGLE_EMAIL", "")
        self.google_password = os.getenv("GOOGLE_PASSWORD", "")
        
        # Colab templates (if creating new notebooks)
        self.colab_templates = {
            "python": "https://colab.research.google.com/github/googlecolab/colabtools/blob/master/notebooks/colab-github-demo.ipynb",
            "empty": "https://colab.research.google.com/#create=true"
        }
        
        # State
        self.current_session_id = None
        self.session_age = 0
        self.total_sessions = 0
        self.mode = "monitor"  # monitor, create_new, upload_code
        
        logger.info("🤖 Complete 24/7 Colab Automation Initialized")
    
    # ================== BROWSER MANAGEMENT ==================
    
    def setup_stealth_browser(self):
        """Setup undetectable browser"""
        try:
            options = uc.ChromeOptions()
            
            # Headless for Render.com
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
            
            # Anti-detection
            options.add_argument("--disable-blink-features=AutomationControlled")
            
            # Create driver
            self.driver = uc.Chrome(options=options)
            
            logger.info("✅ Stealth browser ready")
            return True
            
        except Exception as e:
            logger.error(f"❌ Browser setup failed: {e}")
            return False
    
    def save_cookies(self):
        """Save Google cookies"""
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
    
    # ================== GOOGLE AUTHENTICATION ==================
    
    def google_login(self):
        """Login to Google with saved cookies or credentials"""
        logger.info("🔐 Attempting Google login...")
        
        try:
            # Go to Google
            self.driver.get("https://accounts.google.com")
            time.sleep(3)
            
            # Try cookies first
            if self.load_cookies():
                self.driver.refresh()
                time.sleep(3)
                
                # Check if logged in
                if "myaccount.google.com" in self.driver.current_url:
                    logger.info("✅ Logged in via cookies")
                    return True
            
            # Manual login
            if not self.google_email or not self.google_password:
                logger.error("❌ No credentials for manual login")
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
    
    # ================== COLAB SESSION CREATION ==================
    
    def create_new_colab_session(self):
        """Create a BRAND NEW Colab session from scratch"""
        logger.info("🆕 Creating new Colab session...")
        
        try:
            # Method 1: Use existing notebook URL (if provided)
            if self.colab_notebook_url:
                logger.info(f"📓 Opening existing notebook: {self.colab_notebook_url}")
                self.driver.get(self.colab_notebook_url)
                time.sleep(5)
                
                # Check if we need to copy it
                if "copy" in self.driver.page_source.lower():
                    self.copy_notebook_to_drive()
                else:
                    # Already in our drive, just open
                    pass
                    
            else:
                # Method 2: Create new notebook
                logger.info("📝 Creating new notebook...")
                self.driver.get("https://colab.research.google.com/#create=true")
                time.sleep(5)
                
                # If GitHub Gist URL provided, import from there
                if self.github_gist_url:
                    self.import_from_github_gist()
                else:
                    # Create simple notebook with default cells
                    self.create_default_notebook()
            
            # Connect to runtime
            if not self.connect_runtime():
                logger.warning("⚠️ Could not connect runtime, might need manual intervention")
            
            # Run all cells
            self.run_all_cells()
            
            # Get new session URL
            self.current_session_id = self.driver.current_url
            self.session_start = datetime.now()
            self.total_sessions += 1
            
            logger.info(f"✅ New session created: {self.current_session_id[:80]}...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create new session: {e}")
            return False
    
    def copy_notebook_to_drive(self):
        """Copy notebook to our Google Drive"""
        try:
            # Look for "Copy to Drive" button
            copy_buttons = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Copy to Drive') or contains(text(), 'Save a copy')]")
            
            for button in copy_buttons:
                if button.is_displayed():
                    button.click()
                    logger.info("✅ Clicked 'Copy to Drive'")
                    time.sleep(5)
                    return True
            
            # If no copy button, try File → Save a copy in Drive
            self.driver.find_element(By.XPATH, "//div[text()='File']").click()
            time.sleep(1)
            self.driver.find_element(By.XPATH, "//div[text()='Save a copy in Drive']").click()
            time.sleep(5)
            
            logger.info("✅ Saved copy in Drive")
            return True
            
        except Exception as e:
            logger.warning(f"Could not copy to drive: {e}")
            return False
    
    def import_from_github_gist(self):
        """Import code from GitHub Gist"""
        try:
            # Click File → Open notebook
            self.driver.find_element(By.XPATH, "//div[text()='File']").click()
            time.sleep(1)
            self.driver.find_element(By.XPATH, "//div[text()='Open notebook']").click()
            time.sleep(2)
            
            # Switch to GitHub tab
            github_tab = self.driver.find_element(By.XPATH, "//*[contains(text(), 'GitHub')]")
            github_tab.click()
            time.sleep(2)
            
            # Enter Gist URL
            url_field = self.driver.find_element(By.XPATH, "//input[@placeholder='Enter GitHub URL or search by organization or user']")
            url_field.send_keys(self.github_gist_url)
            url_field.send_keys(Keys.RETURN)
            time.sleep(5)
            
            # Click on the notebook
            notebook_items = self.driver.find_elements(By.XPATH, "//div[@role='listitem']")
            if notebook_items:
                notebook_items[0].click()
                time.sleep(5)
            
            logger.info(f"✅ Imported from Gist: {self.github_gist_url}")
            return True
            
        except Exception as e:
            logger.warning(f"Could not import from Gist: {e}")
            return False
    
    def create_default_notebook(self):
        """Create a default notebook with cells"""
        try:
            # Add a code cell
            self.driver.find_element(By.XPATH, "//div[text()='+ Code']").click()
            time.sleep(2)
            
            # Add some default code
            code_cells = self.driver.find_elements(By.TAG_NAME, "textarea")
            if code_cells:
                code_cell = code_cells[-1]
                
                # Simple keep-alive code
                default_code = '''# Colab 24/7 Automation
import time
from IPython.display import display, Javascript

print("✅ Colab 24/7 Bot - Session Active")

# Keep-alive function
def keep_colab_alive():
    display(Javascript('''
        function clickConnect() {
            console.log("Colab Keep-Alive: " + new Date().toLocaleTimeString());
            if (document.querySelector("colab-connect-button")) {
                document.querySelector("colab-connect-button").click();
            }
        }
        setInterval(clickConnect, 60000);
    '''))

keep_colab_alive()
print("🤖 Keep-alive script activated")'''
                
                code_cell.send_keys(default_code)
                time.sleep(2)
            
            logger.info("✅ Created default notebook")
            return True
            
        except Exception as e:
            logger.warning(f"Could not create default notebook: {e}")
            return False
    
    # ================== COLAB SESSION MANAGEMENT ==================
    
    def connect_runtime(self):
        """Connect to Colab runtime"""
        try:
            # Try multiple button selectors
            selectors = [
                "//*[contains(text(), 'Connect')]",
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
                            logger.info(f"✅ Clicked Connect: {selector}")
                            time.sleep(10)  # Wait for runtime
                            return True
                except:
                    continue
            
            # If no connect button, runtime might already be connected
            return True
            
        except Exception as e:
            logger.error(f"❌ Connect failed: {e}")
            return False
    
    def run_all_cells(self):
        """Run all cells in notebook"""
        try:
            # Method 1: Runtime menu → Run all
            try:
                runtime_menu = self.driver.find_element(By.XPATH, "//div[text()='Runtime']")
                runtime_menu.click()
                time.sleep(1)
                
                run_all_option = self.driver.find_element(By.XPATH, "//div[text()='Run all']")
                run_all_option.click()
                logger.info("✅ Clicked Runtime → Run all")
                time.sleep(5)
                return True
            except:
                pass
            
            # Method 2: Keyboard shortcut Ctrl+F9
            actions = ActionChains(self.driver)
            actions.key_down(Keys.CONTROL).send_keys(Keys.F9).key_up(Keys.CONTROL).perform()
            logger.info("✅ Sent Ctrl+F9 to run all")
            time.sleep(5)
            return True
            
        except Exception as e:
            logger.error(f"❌ Run cells failed: {e}")
            return False
    
    def reset_idle_timer(self):
        """Reset Colab idle timer"""
        try:
            # Simple refresh works
            self.driver.refresh()
            time.sleep(5)
            logger.info("🔄 Refreshed to reset idle timer")
            return True
        except:
            return False
    
    def check_session_status(self):
        """Check if current session is healthy"""
        try:
            page_source = self.driver.page_source.lower()
            
            # Check for disconnection
            if "disconnected" in page_source or "runtime disconnected" in page_source:
                return "disconnected"
            
            # Check for login required
            if "sign in" in page_source or "accounts.google.com" in self.driver.current_url:
                return "login_required"
            
            # Check session age
            if self.session_start:
                self.session_age = (datetime.now() - self.session_start).total_seconds() / 3600
            
            return "healthy"
            
        except Exception as e:
            logger.error(f"❌ Status check failed: {e}")
            return "error"
    
    # ================== MAIN 24/7 AUTOMATION ==================
    
    def full_automation_cycle(self):
        """Complete automation cycle - handles everything"""
        logger.info("🚀 Starting FULL 24/7 Automation Cycle")
        
        cycle_count = 0
        
        while self.is_running:
            try:
                cycle_count += 1
                logger.info(f"🔄 Cycle #{cycle_count}")
                
                # STEP 1: Setup browser if needed
                if not self.driver:
                    if not self.setup_stealth_browser():
                        logger.error("❌ Browser setup failed")
                        time.sleep(60)
                        continue
                
                # STEP 2: Ensure logged in
                if not self.google_login():
                    logger.error("❌ Login failed")
                    time.sleep(60)
                    continue
                
                # STEP 3: Check if we have active session
                if not self.current_session_id or self.session_age > 11.5:
                    # Session expired or doesn't exist - CREATE NEW
                    logger.info("🆕 Creating new session (old session expired or doesn't exist)")
                    if not self.create_new_colab_session():
                        logger.error("❌ Failed to create new session")
                        time.sleep(300)  # Wait 5 minutes before retry
                        continue
                
                else:
                    # STEP 4: We have active session - maintain it
                    logger.info(f"📊 Session age: {self.session_age:.1f}h")
                    
                    # Navigate to current session
                    self.driver.get(self.current_session_id)
                    time.sleep(5)
                    
                    # Check status
                    status = self.check_session_status()
                    
                    if status == "disconnected":
                        logger.warning("⚠️ Session disconnected, reconnecting...")
                        self.connect_runtime()
                        time.sleep(10)
                        
                    elif status == "login_required":
                        logger.warning("⚠️ Login required, re-authenticating...")
                        self.google_login()
                        time.sleep(5)
                        
                    elif status == "healthy":
                        # Reset idle timer periodically
                        if cycle_count % 10 == 0:  # Every ~30 minutes
                            self.reset_idle_timer()
                        logger.info("✅ Session healthy")
                    
                    # Check if session too old
                    if self.session_age > 11.5:  # 11.5 hours
                        logger.warning(f"⏰ Session old ({self.session_age:.1f}h), will restart next cycle")
                
                # STEP 5: Wait for next cycle
                wait_time = 180  # 3 minutes
                logger.info(f"⏳ Next cycle in {wait_time}s")
                time.sleep(wait_time)
                
            except Exception as e:
                logger.error(f"❌ Cycle error: {e}")
                
                # Try to recover
                try:
                    if self.driver:
                        self.driver.quit()
                        self.driver = None
                except:
                    pass
                
                time.sleep(60)  # Wait before retry
    
    def start(self):
        """Start the full automation"""
        if self.is_running:
            logger.warning("⚠️ Already running")
            return False
        
        self.is_running = True
        
        # Start automation in background thread
        thread = threading.Thread(target=self.full_automation_cycle, daemon=True)
        thread.start()
        
        logger.info("✅ 24/7 Complete Automation Started")
        return True
    
    def stop(self):
        """Stop automation"""
        logger.info("🛑 Stopping automation...")
        self.is_running = False
        
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        
        logger.info("📊 Final stats:")
        logger.info(f"   Total sessions created: {self.total_sessions}")
        logger.info(f"   Current session age: {self.session_age:.1f}h")
        
        return True

# ================== WEB DASHBOARD ==================

app = Flask(__name__)
bot = CompleteColabAutomation()

@app.route('/')
def dashboard():
    """Dashboard for monitoring and control"""
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 24/7 Colab Complete Automation</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #0f172a; color: white; }
            .container { max-width: 1000px; margin: 0 auto; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 15px; margin-bottom: 30px; }
            .card { background: #1e293b; padding: 25px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); }
            .btn { background: #10b981; color: white; border: none; padding: 15px 30px; border-radius: 8px; cursor: pointer; margin: 10px; font-size: 16px; }
            .btn:hover { opacity: 0.9; }
            .btn-stop { background: #ef4444; }
            .btn-create { background: #3b82f6; }
            .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
            .stat-box { background: #334155; padding: 20px; border-radius: 10px; text-align: center; }
            .stat-value { font-size: 2em; font-weight: bold; margin: 10px 0; }
            .status-indicator { display: inline-block; width: 15px; height: 15px; border-radius: 50%; margin-right: 10px; }
            .status-online { background: #10b981; animation: pulse 2s infinite; }
            .status-offline { background: #ef4444; }
            @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
            .log { background: #1e293b; padding: 15px; border-radius: 8px; margin: 10px 0; font-family: monospace; overflow: auto; max-height: 200px; }
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
                        document.getElementById('mode').textContent = data.mode;
                        document.getElementById('nextAction').textContent = data.next_action;
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
            
            function forceNewSession() {
                if(confirm('Create brand new Colab session now?')) {
                    fetch('/api/create-new-session')
                        .then(r => r.json())
                        .then(data => {
                            alert(data.message);
                            updateStatus();
                        });
                }
            }
            
            // Auto-update
            setInterval(updateStatus, 5000);
            window.onload = updateStatus;
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 24/7 Colab Complete Automation</h1>
                <p>Creates NEW sessions, uploads code, runs everything automatically</p>
                <p><small>Works even when browser/laptop is closed</small></p>
            </div>
            
            <div class="card">
                <h2>Automation Status: <span id="status">Loading...</span></h2>
                <div class="stats-grid">
                    <div class="stat-box">
                        <div>Current Session Age</div>
                        <div class="stat-value" id="sessionAge">0h</div>
                    </div>
                    <div class="stat-box">
                        <div>Total Sessions Created</div>
                        <div class="stat-value" id="totalSessions">0</div>
                    </div>
                    <div class="stat-box">
                        <div>Current Mode</div>
                        <div class="stat-value" id="mode">-</div>
                    </div>
                    <div class="stat-box">
                        <div>Next Action</div>
                        <div class="stat-value" id="nextAction">-</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>Controls</h2>
                <button class="btn" onclick="control('start')">🚀 Start 24/7 Automation</button>
                <button class="btn btn-stop" onclick="control('stop')">⏹️ Stop Automation</button>
                <button class="btn btn-create" onclick="forceNewSession()">🆕 Force New Session</button>
                <button class="btn" onclick="control('restart')">🔄 Restart Bot</button>
            </div>
            
            <div class="card">
                <h2>What This Bot Does</h2>
                <p>✅ Creates NEW Colab sessions from scratch</p>
                <p>✅ Auto-login with saved cookies</p>
                <p>✅ Imports code from GitHub/Gist (if configured)</p>
                <p>✅ Auto-runs all cells</p>
                <p>✅ Auto-restarts every 11.5 hours</p>
                <p>✅ Works 24/7 even when browser/laptop closed</p>
            </div>
            
            <div class="card">
                <h2>Configuration</h2>
                <p><strong>Colab URL:</strong> {{ colab_url[:50] }}...</p>
                <p><strong>GitHub Gist:</strong> {{ gist_url if gist_url else 'Not set' }}</p>
                <p><strong>Check Interval:</strong> Every 3 minutes</p>
            </div>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html, 
                                 colab_url=bot.colab_notebook_url,
                                 gist_url=bot.github_gist_url)

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "running": bot.is_running,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/status')
def api_status():
    """API status"""
    session_age = bot.session_age if hasattr(bot, 'session_age') else 0
    next_action = f"Restart in {max(0, 11.5 - session_age):.1f}h" if bot.is_running else "Idle"
    
    return jsonify({
        "running": bot.is_running,
        "session_age": f"{session_age:.1f}",
        "total_sessions": bot.total_sessions,
        "mode": bot.mode,
        "next_action": next_action
    })

@app.route('/api/start')
def api_start():
    """Start bot"""
    if bot.is_running:
        return jsonify({"message": "Already running", "success": True})
    
    success = bot.start()
    return jsonify({
        "message": "24/7 Automation started" if success else "Failed to start",
        "success": success
    })

@app.route('/api/stop')
def api_stop():
    """Stop bot"""
    if not bot.is_running:
        return jsonify({"message": "Not running", "success": True})
    
    success = bot.stop()
    return jsonify({
        "message": "Automation stopped" if success else "Failed to stop",
        "success": success
    })

@app.route('/api/create-new-session')
def create_new_session():
    """Force create new session"""
    if not bot.driver:
        return jsonify({"message": "Start bot first", "success": False})
    
    success = bot.create_new_colab_session()
    return jsonify({
        "message": "New session created" if success else "Failed to create session",
        "success": success
    })

# ================== MAIN ==================

def main():
    """Main entry point"""
    print("\n" + "="*70)
    print("🤖 24/7 COLAB COMPLETE AUTOMATION BOT")
    print("="*70)
    print(f"Colab URL: {bot.colab_notebook_url[:50]}..." if bot.colab_notebook_url else "No Colab URL set")
    print(f"GitHub Gist: {bot.github_gist_url[:50]}..." if bot.github_gist_url else "No Gist URL set")
    print("="*70)
    
    # Check for required environment
    if not bot.google_email or not bot.google_password:
        print("⚠️  WARNING: GOOGLE_EMAIL and GOOGLE_PASSWORD not set")
        print("💡 Set these in Render.com environment variables")
        print("💡 Use Google App Password (16 characters)")
    
    # Auto-start on Render.com
    if os.getenv("RENDER"):
        print("🌐 Render.com detected - Starting bot...")
        bot.start()
        
        port = int(os.getenv("PORT", 10000))
        print(f"🌍 Dashboard: http://0.0.0.0:{port}")
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        # Local
        print("💻 Local mode - Manual start required")
        app.run(host='0.0.0.0', port=8080, debug=True)

if __name__ == "__main__":
    main()
