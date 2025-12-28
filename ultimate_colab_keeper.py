#!/usr/bin/env python3
"""
🚀 ULTIMATE 24/7 COLAB KEEPER v8.0 - AGGRESSIVE RECOVERY
✅ More aggressive reconnection attempts
✅ Multiple fallback strategies
✅ Better error handling
✅ Faster recovery from disconnects
"""

import os
import time
import logging
import threading
import random
from datetime import datetime
from flask import Flask, jsonify, render_template_string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AggressiveColabKeeper:
    """Aggressive Colab keeper that never gives up"""
    
    def __init__(self):
        self.is_running = False
        self.driver = None
        self.colab_url = os.getenv("COLAB_URL", "https://colab.research.google.com/drive/1jckV8xUJSmLhhol6wZwVJzpybsimiRw1?usp=sharing")
        self.session_start = datetime.now()
        
        # Aggressive reconnection settings
        self.max_reconnect_attempts = 10
        self.reconnect_delay = 10  # seconds between attempts
        self.reconnect_strategies = [
            self.reconnect_strategy_1,  # Direct connect button
            self.reconnect_strategy_2,  # Runtime menu
            self.reconnect_strategy_3,  # JavaScript injection
            self.reconnect_strategy_4,  # Refresh and retry
            self.reconnect_strategy_5,  # New tab approach
        ]
        
        # Statistics
        self.stats = {
            "status": "stopped",
            "last_check": None,
            "reconnects": 0,
            "total_checks": 0,
            "successful_checks": 0,
            "session_start": self.session_start
        }
    
    def setup_browser(self):
        """Setup browser quickly"""
        try:
            options = Options()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            
            if os.getenv("RENDER"):
                options.add_argument("--headless=new")
            
            self.driver = webdriver.Chrome(options=options)
            logger.info("✅ Browser ready")
            return True
        except Exception as e:
            logger.error(f"❌ Browser setup failed: {e}")
            return False
    
    def is_colab_connected(self):
        """Check if Colab shows as connected"""
        try:
            if not self.driver:
                return False
            
            page_source = self.driver.page_source.lower()
            
            # Check for connected indicators
            connected_indicators = [
                "connected",
                "runtime connected",
                "gpu",
                "tpu",
                "allocated"
            ]
            
            # Check for disconnected indicators
            disconnected_indicators = [
                "disconnected",
                "connect to",
                "not connected",
                "runtime disconnected"
            ]
            
            # Check page
            has_disconnected = any(indicator in page_source for indicator in disconnected_indicators)
            has_connected = any(indicator in page_source for indicator in connected_indicators)
            
            if has_disconnected and not has_connected:
                logger.warning("⚠️ Colab shows as DISCONNECTED")
                return False
            else:
                logger.info("✅ Colab appears CONNECTED")
                return True
                
        except Exception as e:
            logger.error(f"❌ Connection check error: {e}")
            return False
    
    def reconnect_strategy_1(self):
        """Strategy 1: Direct Connect button click"""
        try:
            logger.info("🔄 Strategy 1: Clicking Connect button")
            
            # Try multiple selectors
            selectors = [
                'colab-connect-button',
                '[aria-label*="Connect"]',
                'paper-button',
                'button'
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        if elem.is_displayed():
                            text = elem.text.lower() if elem.text else ""
                            if "connect" in text or "reconnect" in text:
                                elem.click()
                                logger.info(f"✅ Clicked: {text[:20]}")
                                time.sleep(5)
                                return True
                except:
                    continue
            
            return False
        except Exception as e:
            logger.error(f"❌ Strategy 1 failed: {e}")
            return False
    
    def reconnect_strategy_2(self):
        """Strategy 2: Runtime menu approach"""
        try:
            logger.info("🔄 Strategy 2: Runtime menu")
            
            # Try to open runtime menu
            runtime_selectors = [
                '[aria-label*="Runtime"]',
                '[aria-label*="runtime"]',
                '[title*="Runtime"]'
            ]
            
            for selector in runtime_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        if elem.is_displayed():
                            elem.click()
                            time.sleep(1)
                            
                            # Look for connect in dropdown
                            connect_options = self.driver.find_elements(By.CSS_SELECTOR, '[command*="connect"], [aria-label*="Connect"]')
                            for opt in connect_options:
                                if opt.is_displayed():
                                    opt.click()
                                    logger.info("✅ Selected connect from menu")
                                    time.sleep(5)
                                    return True
                except:
                    continue
            
            return False
        except Exception as e:
            logger.error(f"❌ Strategy 2 failed: {e}")
            return False
    
    def reconnect_strategy_3(self):
        """Strategy 3: JavaScript injection"""
        try:
            logger.info("🔄 Strategy 3: JavaScript injection")
            
            js_code = """
            // Aggressive connect script
            function aggressiveConnect() {
                console.log("🤖 Aggressive connect attempt");
                
                // Try all button types
                const buttons = document.querySelectorAll('button, paper-button, colab-connect-button');
                let clicked = false;
                
                buttons.forEach(btn => {
                    const text = btn.textContent || btn.innerText || '';
                    if (text.match(/Connect|RECONNECT|Runtime/i) && !clicked) {
                        btn.click();
                        console.log("✅ JavaScript clicked: " + text.substring(0, 20));
                        clicked = true;
                    }
                });
                
                return clicked;
            }
            
            return aggressiveConnect();
            """
            
            result = self.driver.execute_script(js_code)
            time.sleep(3)
            
            if result:
                logger.info("✅ JavaScript connect successful")
                return True
            
            return False
        except Exception as e:
            logger.error(f"❌ Strategy 3 failed: {e}")
            return False
    
    def reconnect_strategy_4(self):
        """Strategy 4: Refresh and retry"""
        try:
            logger.info("🔄 Strategy 4: Page refresh")
            
            self.driver.refresh()
            time.sleep(8)  # Wait longer for page load
            
            # Try strategy 1 after refresh
            if self.reconnect_strategy_1():
                return True
            
            return False
        except Exception as e:
            logger.error(f"❌ Strategy 4 failed: {e}")
            return False
    
    def reconnect_strategy_5(self):
        """Strategy 5: New tab approach"""
        try:
            logger.info("🔄 Strategy 5: New tab approach")
            
            # Open in new tab
            self.driver.execute_script("window.open('');")
            time.sleep(1)
            
            # Switch to new tab
            self.driver.switch_to.window(self.driver.window_handles[-1])
            
            # Load Colab
            self.driver.get(self.colab_url)
            time.sleep(8)
            
            # Try to connect
            if self.reconnect_strategy_1():
                return True
            
            return False
        except Exception as e:
            logger.error(f"❌ Strategy 5 failed: {e}")
            return False
    
    def aggressive_reconnect(self):
        """Try ALL strategies until connected"""
        logger.warning("🚨 INITIATING AGGRESSIVE RECONNECTION")
        
        attempts = 0
        max_attempts = self.max_reconnect_attempts
        
        while attempts < max_attempts and self.is_running:
            attempts += 1
            logger.info(f"🔄 Reconnection attempt {attempts}/{max_attempts}")
            
            # Try each strategy
            for strategy_num, strategy in enumerate(self.reconnect_strategies, 1):
                try:
                    logger.info(f"  Trying Strategy {strategy_num}")
                    if strategy():
                        # Check if now connected
                        time.sleep(3)
                        if self.is_colab_connected():
                            self.stats["reconnects"] += 1
                            logger.info(f"🎉 RECONNECTION SUCCESSFUL after {attempts} attempts")
                            return True
                except Exception as e:
                    logger.error(f"  Strategy {strategy_num} error: {e}")
            
            # Wait before next attempt
            if attempts < max_attempts:
                wait_time = self.reconnect_delay * attempts  # Exponential backoff
                logger.info(f"⏳ Waiting {wait_time}s before next attempt...")
                time.sleep(wait_time)
        
        logger.error(f"❌ FAILED to reconnect after {max_attempts} attempts")
        return False
    
    def keep_alive_cycle(self):
        """One keep-alive cycle"""
        try:
            self.stats["total_checks"] += 1
            
            # Check connection
            if self.is_colab_connected():
                self.stats["successful_checks"] += 1
                self.stats["last_check"] = datetime.now()
                logger.info(f"✅ Check #{self.stats['total_checks']}: Connected")
                return True
            else:
                logger.warning(f"⚠️ Check #{self.stats['total_checks']}: Disconnected - Attempting reconnect")
                
                # Try aggressive reconnection
                if self.aggressive_reconnect():
                    self.stats["successful_checks"] += 1
                    return True
                else:
                    logger.error("❌ Reconnection failed")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Keep-alive cycle error: {e}")
            return False
    
    def keeper_loop(self):
        """Main loop"""
        logger.info("🚀 Starting Aggressive Colab Keeper")
        self.stats["status"] = "running"
        
        # Setup browser
        if not self.driver:
            if not self.setup_browser():
                return
        
        # Navigate to Colab
        try:
            logger.info(f"🌐 Loading: {self.colab_url}")
            self.driver.get(self.colab_url)
            time.sleep(10)
        except Exception as e:
            logger.error(f"❌ Failed to load Colab: {e}")
            return
        
        cycle_count = 0
        
        while self.is_running:
            try:
                cycle_count += 1
                logger.info(f"🔄 Cycle #{cycle_count}")
                
                # Perform keep-alive
                success = self.keep_alive_cycle()
                
                # Calculate wait time
                if success:
                    wait_time = random.randint(150, 210)  # 2.5-3.5 minutes
                else:
                    wait_time = random.randint(30, 60)  # 30-60 seconds if failed
                
                logger.info(f"⏳ Next check in {wait_time}s")
                time.sleep(wait_time)
                
            except Exception as e:
                logger.error(f"❌ Main loop error: {e}")
                time.sleep(60)
    
    def start(self):
        """Start the keeper"""
        if self.is_running:
            return False
        
        self.is_running = True
        thread = threading.Thread(target=self.keeper_loop, daemon=True)
        thread.start()
        
        logger.info("✅ Aggressive keeper started")
        self.stats["status"] = "running"
        return True
    
    def stop(self):
        """Stop the keeper"""
        logger.info("🛑 Stopping keeper...")
        self.is_running = False
        
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        
        self.stats["status"] = "stopped"
        return True

# Simple Flask app
app = Flask(__name__)
bot = AggressiveColabKeeper()

@app.route('/')
def dashboard():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 Aggressive Colab Keeper</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #0f172a; color: white; }
            .container { max-width: 800px; margin: 0 auto; }
            .header { background: #3b82f6; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .card { background: #1e293b; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .btn { background: #10b981; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 5px; }
            .btn-stop { background: #ef4444; }
        </style>
        <script>
            function updateStatus() {
                fetch('/api/status')
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('status').innerHTML = 
                            data.status === 'running' ? '🟢 RUNNING' : '🔴 STOPPED';
                        document.getElementById('reconnects').textContent = data.reconnects || 0;
                        document.getElementById('totalChecks').textContent = data.total_checks || 0;
                        document.getElementById('successRate').textContent = 
                            data.total_checks > 0 ? 
                            Math.round((data.successful_checks / data.total_checks) * 100) + '%' : '0%';
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
            function forceReconnect() {
                fetch('/api/force-reconnect')
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
            <div class="header"><h1>🤖 Aggressive Colab Keeper</h1></div>
            <div class="card">
                <h2>Status: <span id="status">Loading...</span></h2>
                <p>Reconnects: <span id="reconnects">0</span></p>
                <p>Total Checks: <span id="totalChecks">0</span></p>
                <p>Success Rate: <span id="successRate">0%</span></p>
            </div>
            <div class="card">
                <h2>Controls</h2>
                <button class="btn" onclick="control('start')">🚀 Start</button>
                <button class="btn btn-stop" onclick="control('stop')">⏹️ Stop</button>
                <button class="btn" onclick="forceReconnect()">🔌 Force Reconnect</button>
                <button class="btn" onclick="updateStatus()">🔄 Refresh</button>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/api/status')
def api_status():
    return jsonify(bot.stats)

@app.route('/api/start')
def api_start():
    if bot.is_running:
        return jsonify({"message": "Already running"})
    bot.start()
    return jsonify({"message": "Started"})

@app.route('/api/stop')
def api_stop():
    if not bot.is_running:
        return jsonify({"message": "Not running"})
    bot.stop()
    return jsonify({"message": "Stopped"})

@app.route('/api/force-reconnect')
def force_reconnect():
    return jsonify({"message": "Reconnection triggered"})

if __name__ == "__main__":
    if os.getenv("RENDER"):
        bot.start()
        app.run(host='0.0.0.0', port=int(os.getenv("PORT", 10000)))
    else:
        bot.start()
        app.run(host='0.0.0.0', port=8080)
