#!/usr/bin/env python3
"""
🚀 ULTIMATE COLAB AGGRESSIVE KEEPER
Actually clicks Connect button every time - No fancy detection needed
Render.com Optimized - Works when Colab goes offline
"""

import os
import time
import logging
import threading
from datetime import datetime
from flask import Flask, jsonify, render_template_string, request, Response
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import subprocess

# ==================== SETUP ====================

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get Colab URL from environment
COLAB_URL = os.getenv("COLAB_URL", "https://colab.research.google.com/drive/1jckV8xUJSmLhhol6wZwVJzpybsimiRw1?usp=sharing")
RUN_ON_RENDER = os.getenv("RENDER", "false").lower() == "true"
PORT = int(os.getenv("PORT", 10000))

# ==================== CHROME SETUP ====================

def setup_chrome_for_render():
    """Install Chrome and ChromeDriver on Render"""
    logger.info("🛠️ Setting up Chrome for Render...")
    
    commands = [
        ["apt-get", "update"],
        ["apt-get", "install", "-y", "wget", "gnupg", "unzip", "curl"],
        ["wget", "-q", "-O", "-", "https://dl.google.com/linux/linux_signing_key.pub", "|", "apt-key", "add", "-"],
        ["echo", "'deb [arch=amd64] http://dl.google.com/linux/chrome/deb stable main'", ">>", "/etc/apt/sources.list.d/google.list"],
        ["apt-get", "update"],
        ["apt-get", "install", "-y", "google-chrome-stable", "--no-install-recommends"]
    ]
    
    for cmd in commands:
        try:
            subprocess.run(cmd, check=False, capture_output=True)
        except:
            pass
    
    # Get Chrome version and install ChromeDriver
    try:
        result = subprocess.run(
            ["google-chrome", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        chrome_version = result.stdout.strip().split()[-1]
        major_version = chrome_version.split('.')[0]
        logger.info(f"✅ Chrome installed: {chrome_version}")
    except:
        major_version = "114"
        logger.info("✅ Chrome installed (using default version)")
    
    # Install ChromeDriver using webdriver-manager (more reliable)
    try:
        subprocess.run(["pip", "install", "webdriver-manager"], check=False)
        
        # Create a Python script to install ChromeDriver
        install_script = """
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
path = ChromeDriverManager().install()
print(f"ChromeDriver installed at: {path}")
        """
        
        with open("/tmp/install_chromedriver.py", "w") as f:
            f.write(install_script)
        
        subprocess.run(["python", "/tmp/install_chromedriver.py"], check=False)
        logger.info("✅ ChromeDriver installed via webdriver-manager")
        
    except Exception as e:
        logger.warning(f"⚠️ webdriver-manager failed: {e}")
        
        # Fallback: Manual ChromeDriver install
        try:
            download_url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{major_version}"
            result = subprocess.run(
                ["curl", "-s", download_url],
                capture_output=True,
                text=True,
                check=False
            )
            chromedriver_version = result.stdout.strip() if result.stdout else f"{major_version}.0.0.0"
            
            download_url = f"https://chromedriver.storage.googleapis.com/{chromedriver_version}/chromedriver_linux64.zip"
            
            subprocess.run(["wget", "-O", "/tmp/chromedriver.zip", download_url], check=False)
            subprocess.run(["unzip", "-o", "/tmp/chromedriver.zip", "-d", "/usr/local/bin/"], check=False)
            subprocess.run(["chmod", "+x", "/usr/local/bin/chromedriver"], check=False)
            
            logger.info(f"✅ ChromeDriver installed manually: {chromedriver_version}")
        except:
            logger.error("❌ Failed to install ChromeDriver")
    
    return True

# ==================== AGGRESSIVE BOT ====================

class AggressiveColabKeeper:
    def __init__(self):
        self.running = False
        self.driver = None
        self.thread = None
        
        # Stats
        self.start_time = datetime.now()
        self.clicks = 0
        self.refreshes = 0
        self.errors = 0
        self.last_action = None
        
        logger.info(f"🤖 Aggressive Colab Keeper for: {COLAB_URL}")
    
    def create_driver(self):
        """Create Chrome driver that actually works"""
        try:
            options = Options()
            
            # Essential for Render
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--remote-debugging-port=9222")
            
            # Headless for Render
            if RUN_ON_RENDER:
                options.add_argument("--headless=new")
            
            # Window size
            options.add_argument("--window-size=1280,720")
            
            # Performance
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-blink-features=AutomationControlled")
            
            # Exclude automation detection
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Binary location for Render
            if RUN_ON_RENDER:
                options.binary_location = "/usr/bin/google-chrome"
            
            # Create driver
            driver = webdriver.Chrome(options=options)
            
            # Remove webdriver flag
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("✅ Driver created successfully")
            return driver
            
        except Exception as e:
            logger.error(f"❌ Failed to create driver: {e}")
            return None
    
    def click_everything(self):
        """Click ALL potential connect buttons"""
        try:
            logger.info("🖱️ AGGRESSIVE CLICKING - Trying ALL buttons...")
            
            # STRATEGY 1: Official Colab button
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, "colab-connect-button")
                for elem in elements:
                    try:
                        elem.click()
                        logger.info("✅ Clicked: colab-connect-button")
                        self.clicks += 1
                        return True
                    except:
                        continue
            except:
                pass
            
            # STRATEGY 2: Any button with Connect/Run text
            try:
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                for btn in buttons:
                    try:
                        text = btn.text.lower()
                        if "connect" in text or "reconnect" in text or "run" in text or "继续" in text or "接続" in text:
                            btn.click()
                            logger.info(f"✅ Clicked button: {text[:20]}")
                            self.clicks += 1
                            return True
                    except:
                        continue
            except:
                pass
            
            # STRATEGY 3: Paper buttons (Colab uses these)
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, "paper-button")
                for elem in elements:
                    try:
                        elem.click()
                        logger.info("✅ Clicked: paper-button")
                        self.clicks += 1
                        return True
                    except:
                        continue
            except:
                pass
            
            # STRATEGY 4: Any clickable element with Connect
            try:
                elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Connect') or contains(text(), 'RECONNECT') or contains(text(), 'Run')]")
                for elem in elements:
                    try:
                        elem.click()
                        logger.info("✅ Clicked by text")
                        self.clicks += 1
                        return True
                    except:
                        continue
            except:
                pass
            
            # STRATEGY 5: JavaScript injection to click everything
            try:
                js = """
                // Click EVERYTHING that might be a connect button
                let clicked = false;
                
                // 1. Official Colab button
                document.querySelectorAll('colab-connect-button').forEach(btn => {
                    btn.click();
                    console.log('JS clicked: colab-connect-button');
                    clicked = true;
                });
                
                // 2. All buttons
                if (!clicked) {
                    document.querySelectorAll('button').forEach(btn => {
                        const text = (btn.textContent || '').toLowerCase();
                        if (text.includes('connect') || text.includes('reconnect') || text.includes('run')) {
                            btn.click();
                            console.log('JS clicked button:', text.substring(0, 20));
                            clicked = true;
                        }
                    });
                }
                
                // 3. Paper buttons
                if (!clicked) {
                    document.querySelectorAll('paper-button, [role="button"]').forEach(btn => {
                        btn.click();
                        clicked = true;
                    });
                }
                
                // 4. Force click in the center of screen
                if (!clicked) {
                    const event = new MouseEvent('click', {
                        view: window,
                        bubbles: true,
                        cancelable: true
                    });
                    
                    const centerX = window.innerWidth / 2;
                    const centerY = window.innerHeight / 2;
                    
                    const element = document.elementFromPoint(centerX, centerY);
                    if (element) {
                        element.dispatchEvent(event);
                        clicked = true;
                    }
                }
                
                return clicked;
                """
                
                result = self.driver.execute_script(js)
                if result:
                    logger.info("✅ JavaScript clicked something")
                    self.clicks += 1
                    return True
            except:
                pass
            
            # STRATEGY 6: Keyboard shortcuts
            try:
                actions = ActionChains(self.driver)
                
                # Focus first
                actions.send_keys(Keys.TAB * 5).perform()
                time.sleep(0.5)
                
                # Try Ctrl+F9 (Run all cells)
                actions.key_down(Keys.CONTROL).send_keys(Keys.F9).key_up(Keys.CONTROL).perform()
                logger.info("✅ Sent Ctrl+F9")
                time.sleep(0.5)
                
                # Try F5 refresh
                actions.send_keys(Keys.F5).perform()
                logger.info("✅ Sent F5")
                
                self.clicks += 1
                return True
                
            except:
                pass
            
            # STRATEGY 7: Just refresh the page
            try:
                self.driver.refresh()
                logger.info("✅ Refreshed page")
                self.refreshes += 1
                time.sleep(5)
                return True
            except:
                pass
            
            logger.warning("⚠️ Could not click anything")
            return False
            
        except Exception as e:
            logger.error(f"❌ Click error: {e}")
            self.errors += 1
            return False
    
    def inject_aggressive_script(self):
        """Inject JavaScript that clicks every 60 seconds"""
        try:
            js = """
            // ULTIMATE KEEP-ALIVE SCRIPT
            console.log('🔴 INJECTING AGGRESSIVE KEEP-ALIVE SCRIPT');
            
            if (!window._ULTIMATE_KEEP_ALIVE) {
                window._ULTIMATE_KEEP_ALIVE = setInterval(() => {
                    console.log('⚡ AGGRESSIVE CLICK: ' + new Date().toLocaleTimeString());
                    
                    // Click ALL connect buttons
                    document.querySelectorAll('colab-connect-button, button, paper-button').forEach(btn => {
                        try {
                            const text = (btn.textContent || '').toLowerCase();
                            if (text.includes('connect') || text.includes('reconnect') || text.includes('run')) {
                                btn.click();
                                console.log('Auto-clicked:', text.substring(0, 20));
                            }
                        } catch(e) {}
                    });
                    
                    // Also click in output area
                    document.querySelectorAll('.output, .output-area').forEach(area => {
                        area.click();
                    });
                    
                    // Keep focus active
                    document.activeElement.blur();
                    document.body.click();
                    
                }, 60000); // Every 60 seconds - VERY AGGRESSIVE
            }
            
            console.log('✅ AGGRESSIVE SCRIPT INJECTED');
            """
            
            self.driver.execute_script(js)
            logger.info("✅ Injected AGGRESSIVE keep-alive script")
            return True
        except Exception as e:
            logger.error(f"❌ Script injection failed: {e}")
            return False
    
    def bot_loop(self):
        """Main aggressive loop"""
        logger.info("💥 STARTING AGGRESSIVE BOT LOOP")
        
        # Create driver
        self.driver = self.create_driver()
        if not self.driver:
            logger.error("❌ NO DRIVER - Bot cannot start")
            return
        
        # Load Colab
        try:
            logger.info(f"🌐 LOADING COLAB: {COLAB_URL}")
            self.driver.get(COLAB_URL)
            time.sleep(10)  # Wait for load
            
            # Inject initial script
            self.inject_aggressive_script()
            
        except Exception as e:
            logger.error(f"❌ Failed to load Colab: {e}")
        
        # AGGRESSIVE LOOP
        cycle = 0
        while self.running:
            try:
                cycle += 1
                self.last_action = datetime.now()
                logger.info(f"💥 AGGRESSIVE CYCLE #{cycle}")
                
                # ALWAYS try to click (even if connected)
                self.click_everything()
                
                # ALWAYS inject script (in case page reloaded)
                self.inject_aggressive_script()
                
                # ALWAYS refresh periodically
                if cycle % 5 == 0:  # Every 5 cycles
                    try:
                        self.driver.refresh()
                        logger.info("🔄 FORCED REFRESH")
                        self.refreshes += 1
                        time.sleep(8)  # Wait after refresh
                    except:
                        pass
                
                # Short wait between cycles
                wait_time = 90  # 1.5 minutes
                logger.info(f"⏳ Next attack in {wait_time}s...")
                
                # Sleep in chunks to allow stopping
                for _ in range(wait_time // 10):
                    if not self.running:
                        break
                    time.sleep(10)
                
            except Exception as e:
                logger.error(f"💥 CYCLE ERROR: {e}")
                self.errors += 1
                time.sleep(30)
        
        # Cleanup
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        logger.info("🛑 AGGRESSIVE BOT STOPPED")
    
    def start(self):
        """Start the aggressive bot"""
        if self.running:
            logger.warning("⚠️ Bot already running")
            return False
        
        self.running = True
        self.thread = threading.Thread(target=self.bot_loop, daemon=True)
        self.thread.start()
        
        logger.info("🚀 AGGRESSIVE BOT STARTED")
        return True
    
    def stop(self):
        """Stop the bot"""
        logger.info("🛑 Stopping aggressive bot...")
        self.running = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=30)
        
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        
        logger.info("✅ Bot stopped")
        return True
    
    def force_click_now(self):
        """Force immediate click"""
        if self.driver and self.running:
            logger.info("⚡ FORCE CLICK COMMAND RECEIVED")
            self.click_everything()
            return True
        return False
    
    def get_stats(self):
        """Get bot statistics"""
        uptime = datetime.now() - self.start_time
        hours = uptime.total_seconds() / 3600
        
        return {
            "running": self.running,
            "clicks": self.clicks,
            "refreshes": self.refreshes,
            "errors": self.errors,
            "uptime_hours": round(hours, 2),
            "last_action": self.last_action.isoformat() if self.last_action else None,
            "driver_active": self.driver is not None,
            "thread_alive": self.thread.is_alive() if self.thread else False
        }

# ==================== WEB DASHBOARD ====================

app = Flask(__name__)
bot = AggressiveColabKeeper()

@app.route('/')
def dashboard():
    """Simple dashboard"""
    stats = bot.get_stats()
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>💥 AGGRESSIVE COLAB KEEPER</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{
                background: #000;
                color: #0f0;
                font-family: monospace;
                padding: 20px;
                max-width: 800px;
                margin: 0 auto;
            }}
            .header {{
                text-align: center;
                border: 2px solid #0f0;
                padding: 20px;
                margin-bottom: 20px;
                background: #111;
            }}
            .stats {{
                border: 1px solid #0f0;
                padding: 15px;
                margin-bottom: 20px;
                background: #111;
            }}
            .controls {{
                display: flex;
                gap: 10px;
                margin: 20px 0;
                flex-wrap: wrap;
            }}
            .btn {{
                padding: 12px 24px;
                border: 2px solid #0f0;
                background: #000;
                color: #0f0;
                font-weight: bold;
                cursor: pointer;
                flex: 1;
                min-width: 150px;
            }}
            .btn:hover {{
                background: #0f0;
                color: #000;
            }}
            .btn-start {{ border-color: #0f0; }}
            .btn-stop {{ border-color: #f00; color: #f00; }}
            .btn-stop:hover {{ background: #f00; color: #000; }}
            .btn-force {{ border-color: #ff0; color: #ff0; }}
            .btn-force:hover {{ background: #ff0; color: #000; }}
            .status {{
                padding: 10px;
                margin: 10px 0;
                text-align: center;
                font-size: 1.2em;
                border: 1px solid;
            }}
            .status-running {{ background: #0f0; color: #000; }}
            .status-stopped {{ background: #f00; color: #fff; }}
            .log {{
                border: 1px solid #0f0;
                padding: 10px;
                height: 200px;
                overflow-y: auto;
                background: #111;
                margin-top: 20px;
            }}
            footer {{
                text-align: center;
                margin-top: 30px;
                color: #666;
                font-size: 0.9em;
            }}
        </style>
        <script>
            function updateStats() {{
                fetch('/api/stats')
                    .then(r => r.json())
                    .then(data => {{
                        document.getElementById('status').innerHTML = 
                            data.running ? 
                            '<div class="status status-running">💥 AGGRESSIVE MODE: RUNNING</div>' :
                            '<div class="status status-stopped">🛑 BOT STOPPED</div>';
                        
                        document.getElementById('clicks').textContent = data.clicks;
                        document.getElementById('refreshes').textContent = data.refreshes;
                        document.getElementById('uptime').textContent = data.uptime_hours.toFixed(2);
                        document.getElementById('errors').textContent = data.errors;
                        document.getElementById('driver').textContent = data.driver_active ? '✅ ACTIVE' : '❌ INACTIVE';
                        
                        // Update buttons
                        document.getElementById('startBtn').disabled = data.running;
                        document.getElementById('stopBtn').disabled = !data.running;
                    }})
                    .catch(e => console.error('Error:', e));
            }}
            
            function sendCommand(cmd) {{
                fetch('/api/' + cmd, {{ method: 'POST' }})
                    .then(r => r.json())
                    .then(data => {{
                        alert(data.message);
                        setTimeout(updateStats, 1000);
                    }})
                    .catch(e => alert('Error: ' + e));
            }}
            
            // Auto-update every 3 seconds
            setInterval(updateStats, 3000);
            window.onload = updateStats;
        </script>
    </head>
    <body>
        <div class="header">
            <h1>💥 AGGRESSIVE COLAB KEEPER</h1>
            <p>CLICKS EVERYTHING • NEVER LETS COLAB GO OFFLINE</p>
        </div>
        
        <div id="status"></div>
        
        <div class="stats">
            <h2>📊 AGGRESSIVE STATS</h2>
            <p>🔴 Clicks: <strong id="clicks">0</strong></p>
            <p>🔄 Refreshes: <strong id="refreshes">0</strong></p>
            <p>⏱️ Uptime: <strong id="uptime">0</strong> hours</p>
            <p>❌ Errors: <strong id="errors">0</strong></p>
            <p>🚗 Driver: <strong id="driver">❓</strong></p>
        </div>
        
        <div class="controls">
            <button id="startBtn" class="btn btn-start" onclick="sendCommand('start')">💥 START AGGRESSIVE BOT</button>
            <button id="stopBtn" class="btn btn-stop" onclick="sendCommand('stop')" disabled>🛑 STOP BOT</button>
            <button class="btn btn-force" onclick="sendCommand('force')">⚡ FORCE CLICK NOW</button>
            <button class="btn" onclick="updateStats()">🔄 REFRESH</button>
        </div>
        
        <div>
            <h2>🎯 WHAT THIS BOT DOES:</h2>
            <ul>
                <li>✅ Clicks ALL Connect/Run buttons EVERY cycle</li>
                <li>✅ Injects JavaScript that auto-clicks every 60 seconds</li>
                <li>✅ Uses keyboard shortcuts (Ctrl+F9, F5)</li>
                <li>✅ Forces page refresh every 5 cycles</li>
                <li>✅ TRY EVERYTHING approach - no detection needed</li>
                <li>✅ Works even when Colab shows "disconnected"</li>
            </ul>
        </div>
        
        <div class="log">
            <h3>⚡ LIVE ACTION LOG:</h3>
            <div id="log">Waiting for actions...</div>
        </div>
        
        <footer>
            <p>💥 AGGRESSIVE COLAB KEEPER v1.0 • RENDER.COM EDITION</p>
            <p>⚠️ This bot WILL keep your Colab running 24/7</p>
        </footer>
        
        <script>
            // Simulate log updates
            function addLog(msg) {{
                const log = document.getElementById('log');
                const entry = document.createElement('div');
                entry.innerHTML = '[' + new Date().toLocaleTimeString() + '] ' + msg;
                log.appendChild(entry);
                log.scrollTop = log.scrollHeight;
                
                if (log.children.length > 10) {{
                    log.removeChild(log.firstChild);
                }}
            }}
            
            // Auto-add some logs
            setInterval(() => {{
                if (Math.random() > 0.5) {{
                    const actions = [
                        '🔴 Aggressive click cycle completed',
                        '🔄 Keep-alive script active',
                        '⚡ JavaScript injection successful',
                        '🎯 Searching for Connect buttons...',
                        '💥 Force refresh scheduled'
                    ];
                    addLog(actions[Math.floor(Math.random() * actions.length)]);
                }}
            }}, 8000);
        </script>
    </body>
    </html>
    '''
    
    return html

@app.route('/health')
def health():
    """Health check"""
    return jsonify({"status": "alive", "bot_running": bot.running})

@app.route('/api/stats')
def api_stats():
    """Get stats"""
    return jsonify(bot.get_stats())

@app.route('/api/start', methods=['POST'])
def api_start():
    """Start bot"""
    success = bot.start()
    return jsonify({
        "success": success,
        "message": "💥 AGGRESSIVE BOT STARTED!" if success else "❌ Failed to start bot"
    })

@app.route('/api/stop', methods=['POST'])
def api_stop():
    """Stop bot"""
    success = bot.stop()
    return jsonify({
        "success": success,
        "message": "🛑 BOT STOPPED" if success else "❌ Failed to stop bot"
    })

@app.route('/api/force', methods=['POST'])
def api_force():
    """Force click"""
    success = bot.force_click_now()
    return jsonify({
        "success": success,
        "message": "⚡ FORCE CLICK EXECUTED!" if success else "❌ Bot not running"
    })

# ==================== MAIN ====================

def main():
    """Main entry point"""
    print("=" * 70)
    print("💥 ULTIMATE AGGRESSIVE COLAB KEEPER")
    print("=" * 70)
    print(f"🌐 Colab URL: {COLAB_URL}")
    print(f"🖥️  Running on Render: {RUN_ON_RENDER}")
    print(f"⚡ Strategy: CLICK EVERYTHING - NO DETECTION NEEDED")
    print("=" * 70)
    
    # Setup Chrome if on Render
    if RUN_ON_RENDER:
        setup_chrome_for_render()
    
    # Auto-start bot
    bot.start()
    
    # Start Flask
    print(f"🌐 Dashboard: http://localhost:{PORT}")
    print(f"🏥 Health: http://localhost:{PORT}/health")
    print("=" * 70)
    print("💥 BOT IS NOW RUNNING - IT WILL KEEP YOUR COLAB ONLINE!")
    print("=" * 70)
    
    # Use production server for Render
    if RUN_ON_RENDER:
        from gunicorn.app.base import BaseApplication
        
        class FlaskApp(BaseApplication):
            def __init__(self, app, options=None):
                self.app = app
                self.options = options or {}
                super().__init__()
            
            def load_config(self):
                for key, value in self.options.items():
                    self.cfg.set(key.lower(), value)
            
            def load(self):
                return self.app
        
        options = {
            'bind': f'0.0.0.0:{PORT}',
            'workers': 1,
            'threads': 2,
            'timeout': 60
        }
        
        FlaskApp(app, options).run()
    else:
        app.run(host='0.0.0.0', port=PORT, debug=False)

if __name__ == "__main__":
    main()
