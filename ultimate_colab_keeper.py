#!/usr/bin/env python3
"""
🚀 REAL COLAB KEEPER - ACTUALLY CLICKS & RUNS
✅ Actually clicks Connect button
✅ Actually runs cells
✅ Actually keeps Colab online
"""

import os
import time
import logging
import threading
from datetime import datetime
from flask import Flask, jsonify, render_template_string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class RealColabKeeper:
    def __init__(self):
        self.is_running = False
        self.driver = None
        
        # Your Colab URL
        self.colab_url = "https://colab.research.google.com/drive/1jckV8xUJSmLhhol6wZwVJzpybsimiRw1?usp=sharing"
        
        # Stats
        self.actions = 0
        self.connects = 0
        self.cells_run = 0
        self.session_start = datetime.now()
        
        logger.info(f"🤖 REAL Colab Keeper for: {self.colab_url}")
    
    def setup_browser(self):
        """Setup Chrome to actually interact"""
        try:
            options = Options()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            # Remove for debugging, but needed for Render
            if os.getenv("RENDER"):
                options.add_argument("--headless=new")
            
            # Essential for clicking
            options.add_argument("--window-size=1920,1080")
            
            self.driver = webdriver.Chrome(options=options)
            logger.info("✅ Browser ready for clicking")
            return True
        except Exception as e:
            logger.error(f"❌ Browser setup failed: {e}")
            return False
    
    def actually_click_connect(self):
        """ACTUALLY click the Connect button"""
        try:
            logger.info("🖱️ Looking for Connect button to ACTUALLY click...")
            
            # Strategy 1: Find by visible text
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for btn in buttons:
                try:
                    text = btn.text
                    if text and ("Connect" in text or "RECONNECT" in text):
                        if btn.is_displayed():
                            btn.click()
                            logger.info(f"✅ ACTUALLY clicked: {text}")
                            self.connects += 1
                            time.sleep(5)
                            return True
                except:
                    continue
            
            # Strategy 2: Find by selector
            selectors = [
                'colab-connect-button',
                '[aria-label*="Connect"]',
                'paper-button'
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        if elem.is_displayed():
                            elem.click()
                            logger.info(f"✅ ACTUALLY clicked using selector: {selector}")
                            self.connects += 1
                            time.sleep(5)
                            return True
                except:
                    continue
            
            # Strategy 3: JavaScript click
            js = """
            var clicked = false;
            var buttons = document.querySelectorAll('button, colab-connect-button, paper-button');
            buttons.forEach(btn => {
                var text = btn.textContent || '';
                if (text.includes('Connect') || text.includes('RECONNECT')) {
                    btn.click();
                    console.log('🤖 JavaScript ACTUALLY clicked Connect');
                    clicked = true;
                }
            });
            return clicked;
            """
            
            result = self.driver.execute_script(js)
            if result:
                logger.info("✅ JavaScript ACTUALLY clicked Connect")
                self.connects += 1
                time.sleep(5)
                return True
            
            logger.warning("⚠️ Could not find Connect button")
            return False
            
        except Exception as e:
            logger.error(f"❌ Click error: {e}")
            return False
    
    def actually_run_cells(self):
        """ACTUALLY run cells with Ctrl+F9"""
        try:
            logger.info("▶️ Trying to ACTUALLY run cells...")
            
            # Press Ctrl+F9 to run all
            actions = ActionChains(self.driver)
            actions.key_down(Keys.CONTROL).send_keys(Keys.F9).key_up(Keys.CONTROL).perform()
            
            logger.info("✅ Sent Ctrl+F9 to ACTUALLY run cells")
            self.cells_run += 1
            time.sleep(5)
            return True
        except Exception as e:
            logger.error(f"❌ Run cells error: {e}")
            return False
    
    def inject_keepalive_script(self):
        """Inject JavaScript to keep Colab alive"""
        try:
            js = """
            // REAL keep-alive script
            function realKeepAlive() {
                console.log("🔄 REAL Keep-Alive: " + new Date().toLocaleTimeString());
                
                // Find and click Connect
                var buttons = document.querySelectorAll('colab-connect-button, button, paper-button');
                buttons.forEach(btn => {
                    var text = btn.textContent || '';
                    if (text.includes('Connect') || text.includes('RECONNECT')) {
                        btn.click();
                        console.log('✅ Injected script clicked Connect');
                    }
                });
                
                // Also click in output area
                var outputs = document.querySelectorAll('.output');
                if (outputs.length > 0) {
                    outputs[0].click();
                }
            }
            
            // Run every 80 seconds
            setInterval(realKeepAlive, 80000);
            realKeepAlive(); // Run now
            console.log("🎉 REAL keep-alive injected");
            """
            
            self.driver.execute_script(js)
            logger.info("✅ Injected REAL keep-alive script")
            return True
        except Exception as e:
            logger.error(f"❌ Script injection error: {e}")
            return False
    
    def perform_real_actions(self):
        """Perform ACTUAL actions to keep Colab alive"""
        try:
            self.actions += 1
            logger.info(f"🎯 REAL Action #{self.actions}")
            
            # 1. Click Connect if needed
            self.actually_click_connect()
            
            # 2. Run cells
            self.actually_run_cells()
            
            # 3. Inject keep-alive
            self.inject_keepalive_script()
            
            # 4. Simple refresh
            self.driver.refresh()
            time.sleep(5)
            
            logger.info(f"✅ Completed REAL action #{self.actions}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Action error: {e}")
            return False
    
    def keep_alive_loop(self):
        """Main loop with REAL actions"""
        logger.info("🚀 Starting REAL keeper loop")
        
        # Setup browser
        if not self.driver:
            if not self.setup_browser():
                logger.error("❌ Failed to setup browser")
                return
        
        # Load Colab
        try:
            logger.info(f"🌐 Loading Colab...")
            self.driver.get(self.colab_url)
            time.sleep(10)
            logger.info("✅ Colab loaded")
        except Exception as e:
            logger.error(f"❌ Failed to load Colab: {e}")
            return
        
        while self.is_running:
            try:
                # Perform REAL actions
                self.perform_real_actions()
                
                # Wait 2.5 minutes
                wait_time = 150
                logger.info(f"⏳ Next REAL action in {wait_time//60} minutes")
                time.sleep(wait_time)
                
            except Exception as e:
                logger.error(f"❌ Loop error: {e}")
                time.sleep(60)
    
    def start(self):
        """Start the REAL keeper"""
        if self.is_running:
            return False
        
        self.is_running = True
        thread = threading.Thread(target=self.keep_alive_loop, daemon=True)
        thread.start()
        
        logger.info("✅ REAL keeper started")
        return True
    
    def stop(self):
        """Stop the keeper"""
        logger.info("🛑 Stopping REAL keeper")
        self.is_running = False
        
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        
        return True

# Flask app
app = Flask(__name__)
bot = RealColabKeeper()

@app.route('/')
def dashboard():
    session_age = datetime.now() - bot.session_start
    minutes = int(session_age.total_seconds() / 60)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 REAL Colab Keeper</title>
        <style>
            body {{ font-family: Arial; padding: 20px; background: #0f172a; color: white; }}
            .status {{ font-size: 1.5em; margin: 20px 0; }}
            .stats {{ background: #1e293b; padding: 15px; border-radius: 10px; margin: 10px 0; }}
            .btn {{ background: #10b981; color: white; border: none; padding: 10px 20px; margin: 5px; border-radius: 5px; cursor: pointer; }}
            .btn-stop {{ background: #ef4444; }}
        </style>
        <script>
            function update() {{
                fetch('/api/status')
                    .then(r => r.json())
                    .then(data => {{
                        document.getElementById('status').innerHTML = 
                            data.running ? '🟢 REAL KEEPER RUNNING' : '🔴 STOPPED';
                        document.getElementById('actions').textContent = data.actions;
                        document.getElementById('connects').textContent = data.connects;
                        document.getElementById('cells').textContent = data.cells_run;
                        document.getElementById('time').textContent = data.session_age;
                    }});
            }}
            setInterval(update, 5000);
            window.onload = update;
        </script>
    </head>
    <body>
        <h1>🤖 REAL Colab Keeper</h1>
        <p>Actually clicks buttons & runs cells</p>
        
        <div class="stats">
            <div class="status" id="status">Loading...</div>
            <p>Real Actions: <strong id="actions">0</strong></p>
            <p>Connect Clicks: <strong id="connects">0</strong></p>
            <p>Cells Run: <strong id="cells">0</strong></p>
            <p>Session: <strong id="time">0m</strong></p>
        </div>
        
        <div>
            <button class="btn" onclick="window.location.href='/start'">▶️ Start REAL Keeper</button>
            <button class="btn btn-stop" onclick="window.location.href='/stop'">⏹️ Stop</button>
            <button class="btn" onclick="window.location.href='{bot.colab_url}'" target="_blank">📓 Open Colab</button>
        </div>
        
        <div style="margin-top: 30px; background: #334155; padding: 15px; border-radius: 10px;">
            <h3>🎯 What this bot ACTUALLY does:</h3>
            <ul>
                <li>✅ Actually clicks Connect button</li>
                <li>✅ Actually runs cells (Ctrl+F9)</li>
                <li>✅ Actually injects keep-alive script</li>
                <li>✅ Actually refreshes page</li>
                <li>✅ Every 2.5 minutes</li>
            </ul>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "running": bot.is_running})

@app.route('/api/status')
def api_status():
    session_age = datetime.now() - bot.session_start
    minutes = int(session_age.total_seconds() / 60)
    
    return jsonify({
        "running": bot.is_running,
        "actions": bot.actions,
        "connects": bot.connects,
        "cells_run": bot.cells_run,
        "session_age": f"{minutes}m"
    })

@app.route('/start')
def start():
    bot.start()
    return "✅ REAL keeper started. <a href='/'>Back to dashboard</a>"

@app.route('/stop')
def stop():
    bot.stop()
    return "🛑 REAL keeper stopped. <a href='/'>Back to dashboard</a>"

if __name__ == "__main__":
    # Auto-start on Render
    if os.getenv("RENDER"):
        bot.start()
        app.run(host='0.0.0.0', port=int(os.getenv("PORT", 10000)))
    else:
        bot.start()
        app.run(host='0.0.0.0', port=8080)
