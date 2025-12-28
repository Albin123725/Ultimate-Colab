#!/usr/bin/env python3
"""
🚀 AI COLAB SUPREME - RENDER.COM EDITION
Single file deployment with all features
Version: 3.1.0 | Render Optimized
"""

import os
import sys
import time
import json
import asyncio
import logging
import threading
import random
import string
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import signal
import subprocess
import traceback

# Core imports
from flask import Flask, jsonify, render_template_string, request, Response
from prometheus_client import Counter, Gauge, Histogram, generate_latest
import psutil

# Try to import optional AI modules
try:
    import numpy as np
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("⚠️ numpy not installed - AI features disabled")

# Try Selenium
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("❌ Selenium not installed - browser automation disabled")

# ==================== CONFIGURATION ====================

class Config:
    DEFAULTS = {
        "COLAB_URL": os.getenv("COLAB_URL", "https://colab.research.google.com/drive/"),
        "RENDER": os.getenv("RENDER", "false").lower() == "true",
        "PORT": int(os.getenv("PORT", 8080)),
        
        # Bot settings
        "CHECK_INTERVAL": 180,  # 3 minutes
        "MAX_RETRIES": 5,
        "MAX_TABS": 1,  # Reduced for Render free tier
        
        # Features
        "ENABLE_AI": os.getenv("ENABLE_AI", "false").lower() == "true",
        "ENABLE_CV": os.getenv("ENABLE_CV", "false").lower() == "true",
        "HEADLESS": True,
        "AUTO_START": True,
        
        # Monitoring
        "LOG_LEVEL": "INFO",
        "HEALTH_CHECK": True,
        
        # Render optimization
        "MEMORY_LIMIT_MB": 512,
        "TIMEOUT_SECONDS": 300,
    }
    
    @classmethod
    def get(cls, key):
        return os.getenv(key, cls.DEFAULTS.get(key))

# ==================== LOGGING ====================

def setup_logger():
    logger = logging.getLogger("ColabBot")
    log_level = getattr(logging, Config.get("LOG_LEVEL"), logging.INFO)
    
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # Configure handlers
    handlers = []
    
    # File handler
    file_handler = logging.FileHandler(f"logs/colab_bot_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler.setLevel(log_level)
    handlers.append(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    handlers.append(console_handler)
    
    # Format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    for handler in handlers:
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    logger.setLevel(log_level)
    return logger

logger = setup_logger()

# ==================== BROWSER SETUP ====================

def setup_chrome():
    """Setup Chrome for Render.com"""
    logger.info("Setting up Chrome for Render...")
    
    try:
        # Install Chrome on Render
        if Config.get("RENDER"):
            logger.info("Running on Render.com - installing Chrome...")
            
            # Install Chrome
            subprocess.run([
                "apt-get", "update"
            ], check=False)
            
            subprocess.run([
                "apt-get", "install", "-y", "wget", "gnupg", "unzip"
            ], check=False)
            
            # Download and install Chrome
            subprocess.run([
                "wget", "-q", "-O", "-", 
                "https://dl.google.com/linux/linux_signing_key.pub"
            ], check=False)
            
            subprocess.run([
                "sh", "-c", 
                "echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb stable main' >> /etc/apt/sources.list.d/google.list"
            ], check=False)
            
            subprocess.run([
                "apt-get", "update"
            ], check=False)
            
            subprocess.run([
                "apt-get", "install", "-y", "google-chrome-stable"
            ], check=False)
            
            # Get Chrome version and install ChromeDriver
            result = subprocess.run(
                ["google-chrome", "--version"],
                capture_output=True,
                text=True
            )
            
            chrome_version = result.stdout.strip().split()[-1]
            major_version = chrome_version.split('.')[0]
            
            logger.info(f"Chrome version: {chrome_version}")
            
            # Download matching ChromeDriver
            chromedriver_url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{major_version}"
            
            try:
                response = subprocess.run(
                    ["curl", "-s", chromedriver_url],
                    capture_output=True,
                    text=True,
                    check=True
                )
                chromedriver_version = response.stdout.strip()
            except:
                chromedriver_version = major_version + ".0.0"
            
            download_url = f"https://chromedriver.storage.googleapis.com/{chromedriver_version}/chromedriver_linux64.zip"
            
            logger.info(f"Downloading ChromeDriver from: {download_url}")
            
            subprocess.run([
                "wget", "-O", "/tmp/chromedriver.zip", download_url
            ], check=False)
            
            subprocess.run([
                "unzip", "/tmp/chromedriver.zip", "-d", "/usr/local/bin/"
            ], check=False)
            
            subprocess.run([
                "chmod", "+x", "/usr/local/bin/chromedriver"
            ], check=False)
            
            logger.info("✅ Chrome setup complete on Render")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Chrome setup failed: {e}")
        return False

def create_driver():
    """Create Chrome driver optimized for Render"""
    if not SELENIUM_AVAILABLE:
        logger.error("Selenium not available")
        return None
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        
        # Render-specific optimizations
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-accelerated-2d-canvas")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Memory optimizations
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--memory-pressure-off")
        
        # Headless mode for Render
        if Config.get("HEADLESS"):
            options.add_argument("--headless=new")
        
        # Window size
        options.add_argument("--window-size=1280,720")
        
        # Performance arguments
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-features=TranslateUI")
        options.add_argument("--disable-component-extensions-with-background-pages")
        
        # Experimental options
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Set binary location for Render
        if Config.get("RENDER"):
            options.binary_location = "/usr/bin/google-chrome"
        
        # Create driver
        driver = webdriver.Chrome(options=options)
        
        # Execute stealth script
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        logger.info("✅ Chrome driver created")
        return driver
        
    except Exception as e:
        logger.error(f"❌ Failed to create driver: {e}")
        return None

# ==================== CORE BOT ====================

class ColabBot:
    def __init__(self):
        self.state = "stopped"
        self.driver = None
        self.colab_url = Config.get("COLAB_URL")
        self.metrics = {
            "start_time": datetime.now(),
            "total_checks": 0,
            "successful_checks": 0,
            "failed_checks": 0,
            "last_success": None,
            "last_error": None
        }
        self.running = False
        self.thread = None
        
        # Prometheus metrics
        self.prom_total_checks = Counter('colab_total_checks', 'Total checks performed')
        self.prom_successful_checks = Counter('colab_successful_checks', 'Successful checks')
        self.prom_failed_checks = Counter('colab_failed_checks', 'Failed checks')
        self.prom_bot_state = Gauge('colab_bot_state', 'Bot state', ['state'])
        
        logger.info(f"🤖 Colab Bot initialized for: {self.colab_url}")
    
    def click_connect_button(self):
        """Click Connect button using multiple strategies"""
        if not self.driver:
            return False
        
        try:
            strategies = [
                self._click_by_aria_label,
                self._click_by_button_text,
                self._click_by_css_selector,
                self._click_by_xpath,
                self._click_by_javascript,
                self._keyboard_shortcut
            ]
            
            for strategy in strategies:
                if strategy():
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Click error: {e}")
            return False
    
    def _click_by_aria_label(self):
        """Click by aria-label"""
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, '[aria-label*="Connect"], [aria-label*="RECONNECT"]')
            for element in elements:
                if element.is_displayed():
                    element.click()
                    logger.info("✅ Clicked by aria-label")
                    return True
        except:
            pass
        return False
    
    def _click_by_button_text(self):
        """Click by button text"""
        try:
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                try:
                    text = button.text.lower()
                    if "connect" in text or "reconnect" in text or "run" in text:
                        if button.is_displayed():
                            button.click()
                            logger.info("✅ Clicked by button text")
                            return True
                except:
                    continue
        except:
            pass
        return False
    
    def _click_by_css_selector(self):
        """Click by CSS selector"""
        selectors = [
            "colab-connect-button",
            "paper-button",
            ".connect-button",
            "[role='button']"
        ]
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed():
                        element.click()
                        logger.info(f"✅ Clicked by selector: {selector}")
                        return True
            except:
                continue
        return False
    
    def _click_by_xpath(self):
        """Click by XPath"""
        xpaths = [
            "//button[contains(text(), 'Connect')]",
            "//button[contains(text(), 'RECONNECT')]",
            "//button[contains(text(), 'Run')]",
            "//*[contains(@aria-label, 'Connect')]"
        ]
        
        for xpath in xpaths:
            try:
                elements = self.driver.find_elements(By.XPATH, xpath)
                for element in elements:
                    if element.is_displayed():
                        element.click()
                        logger.info(f"✅ Clicked by XPath: {xpath}")
                        return True
            except:
                continue
        return False
    
    def _click_by_javascript(self):
        """Click using JavaScript"""
        try:
            js_code = """
            function clickConnect() {
                let clicked = false;
                
                // Try different methods
                const methods = [
                    () => document.querySelectorAll('button').forEach(btn => {
                        const text = (btn.textContent || '').toLowerCase();
                        if (text.includes('connect') || text.includes('reconnect')) {
                            btn.click();
                            clicked = true;
                        }
                    }),
                    () => document.querySelectorAll('[role="button"]').forEach(btn => btn.click()),
                    () => document.querySelectorAll('paper-button').forEach(btn => btn.click()),
                    () => {
                        const event = new MouseEvent('click', {bubbles: true});
                        document.querySelectorAll('colab-connect-button').forEach(el => {
                            el.dispatchEvent(event);
                            clicked = true;
                        });
                    }
                ];
                
                methods.forEach(method => {
                    if (!clicked) method();
                });
                
                return clicked;
            }
            
            return clickConnect();
            """
            
            result = self.driver.execute_script(js_code)
            if result:
                logger.info("✅ Clicked by JavaScript")
            return bool(result)
        except:
            return False
    
    def _keyboard_shortcut(self):
        """Use keyboard shortcuts"""
        try:
            actions = ActionChains(self.driver)
            
            # Try various shortcuts
            shortcuts = [
                (Keys.CONTROL, Keys.F9),  # Run all
                (Keys.CONTROL, Keys.ENTER),  # Run cell
                (Keys.F5,),  # Refresh
                (Keys.CONTROL, 'r'),  # Refresh
            ]
            
            for shortcut in shortcuts:
                try:
                    actions = ActionChains(self.driver)
                    for key in shortcut[:-1]:
                        actions.key_down(key)
                    actions.send_keys(shortcut[-1])
                    for key in shortcut[:-1]:
                        actions.key_up(key)
                    actions.perform()
                    logger.info(f"✅ Keyboard shortcut: {shortcut}")
                    return True
                except:
                    continue
        except:
            pass
        return False
    
    def inject_keepalive_script(self):
        """Inject keep-alive JavaScript"""
        try:
            js_code = """
            // Keep-alive script for Colab
            if (!window._colabKeepAlive) {
                window._colabKeepAlive = setInterval(() => {
                    console.log('🔄 Keep-alive ping: ' + new Date().toLocaleTimeString());
                    
                    // Click any connect buttons
                    document.querySelectorAll('button, colab-connect-button, paper-button').forEach(btn => {
                        const text = (btn.textContent || '').toLowerCase();
                        if (text.includes('connect') || text.includes('reconnect')) {
                            btn.click();
                            console.log('✅ Auto-clicked');
                        }
                    });
                    
                    // Keep focus
                    document.activeElement.blur();
                    document.querySelector('body').click();
                    
                }, 85000); // 85 seconds (before 90-minute timeout)
                
                console.log('✅ Keep-alive script injected');
            }
            """
            
            self.driver.execute_script(js_code)
            logger.info("✅ Injected keep-alive script")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to inject script: {e}")
            return False
    
    def check_connection(self):
        """Check if Colab is connected"""
        try:
            # Look for disconnect indicators
            disconnect_indicators = [
                "Runtime disconnected",
                "Connect to runtime",
                "Not connected",
                "disconnected"
            ]
            
            page_source = self.driver.page_source.lower()
            
            for indicator in disconnect_indicators:
                if indicator.lower() in page_source:
                    return False
            
            # Look for connect indicators
            connect_indicators = ["connect", "reconnect", "connect to runtime"]
            
            for indicator in connect_indicators:
                if indicator.lower() in page_source:
                    # Try to click it
                    return self.click_connect_button()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Connection check error: {e}")
            return False
    
    def run_check_cycle(self):
        """Run a single check cycle"""
        try:
            logger.info("🔄 Running check cycle...")
            
            # Check connection
            is_connected = self.check_connection()
            
            if not is_connected:
                logger.warning("⚠️ Colab disconnected, attempting to reconnect...")
                
                # Try multiple click strategies
                clicked = self.click_connect_button()
                
                if clicked:
                    logger.info("✅ Successfully clicked Connect")
                else:
                    logger.warning("⚠️ Could not find Connect button")
                    
                    # Try refresh
                    try:
                        self.driver.refresh()
                        time.sleep(5)
                        self.click_connect_button()
                    except:
                        pass
            
            # Inject keep-alive script
            self.inject_keepalive_script()
            
            # Update metrics
            self.metrics["total_checks"] += 1
            
            if is_connected or clicked:
                self.metrics["successful_checks"] += 1
                self.metrics["last_success"] = datetime.now()
                self.prom_successful_checks.inc()
                logger.info("✅ Check cycle successful")
            else:
                self.metrics["failed_checks"] += 1
                self.metrics["last_error"] = datetime.now()
                self.prom_failed_checks.inc()
                logger.warning("⚠️ Check cycle failed")
            
            self.prom_total_checks.inc()
            return True
            
        except Exception as e:
            logger.error(f"❌ Check cycle error: {e}")
            self.metrics["failed_checks"] += 1
            self.metrics["last_error"] = datetime.now()
            self.prom_failed_checks.inc()
            return False
    
    def bot_loop(self):
        """Main bot loop"""
        logger.info("🚀 Starting bot loop...")
        
        # Initialize driver
        self.driver = create_driver()
        if not self.driver:
            logger.error("❌ Failed to create driver")
            self.state = "error"
            return
        
        try:
            # Load Colab
            logger.info(f"🌐 Loading Colab: {self.colab_url}")
            self.driver.get(self.colab_url)
            time.sleep(10)  # Wait for page load
            
            # Inject initial script
            self.inject_keepalive_script()
            
            self.state = "running"
            logger.info("✅ Bot started successfully")
            
            # Main loop
            while self.running:
                try:
                    # Run check cycle
                    self.run_check_cycle()
                    
                    # Calculate next check time
                    check_interval = Config.get("CHECK_INTERVAL")
                    
                    # Adaptive interval based on success rate
                    success_rate = (self.metrics["successful_checks"] / 
                                  max(self.metrics["total_checks"], 1))
                    
                    if success_rate > 0.9:
                        interval = check_interval * 1.5  # Reduce frequency if successful
                    elif success_rate > 0.7:
                        interval = check_interval
                    else:
                        interval = check_interval * 0.7  # Increase frequency if failing
                    
                    # Add some randomness
                    interval += random.uniform(-10, 10)
                    interval = max(60, min(interval, 300))  # Keep between 1-5 minutes
                    
                    logger.info(f"⏳ Next check in {interval:.0f}s")
                    
                    # Sleep in chunks to allow for interruption
                    sleep_interval = 10  # Check every 10 seconds if we should stop
                    total_slept = 0
                    
                    while total_slept < interval and self.running:
                        time.sleep(min(sleep_interval, interval - total_slept))
                        total_slept += sleep_interval
                    
                except Exception as e:
                    logger.error(f"❌ Loop error: {e}")
                    time.sleep(30)  # Wait before retry
        
        except Exception as e:
            logger.error(f"❌ Bot loop fatal error: {e}")
            self.state = "error"
        
        finally:
            # Cleanup
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
            
            self.state = "stopped"
            logger.info("🛑 Bot stopped")
    
    def start(self):
        """Start the bot"""
        if self.state == "running":
            logger.warning("⚠️ Bot already running")
            return False
        
        if not SELENIUM_AVAILABLE:
            logger.error("❌ Selenium not available")
            return False
        
        self.running = True
        self.state = "starting"
        
        # Start bot in separate thread
        self.thread = threading.Thread(target=self.bot_loop, daemon=True)
        self.thread.start()
        
        logger.info("✅ Bot start command sent")
        return True
    
    def stop(self):
        """Stop the bot"""
        logger.info("🛑 Stopping bot...")
        self.running = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=30)
        
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
        
        self.state = "stopped"
        logger.info("✅ Bot stopped")
        return True
    
    def get_status(self):
        """Get bot status"""
        status = {
            "state": self.state,
            "running": self.running,
            "metrics": self.metrics.copy(),
            "uptime": str(datetime.now() - self.metrics["start_time"]),
            "success_rate": (self.metrics["successful_checks"] / 
                           max(self.metrics["total_checks"], 1)) * 100,
            "driver_active": self.driver is not None,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add system info
        try:
            status["system"] = {
                "memory_mb": psutil.Process().memory_info().rss / 1024 / 1024,
                "cpu_percent": psutil.cpu_percent(),
                "thread_alive": self.thread.is_alive() if self.thread else False
            }
        except:
            pass
        
        return status

# ==================== FLASK APP ====================

app = Flask(__name__)
bot = ColabBot()

@app.route('/')
def dashboard():
    """Main dashboard"""
    status = bot.get_status()
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 Colab Supreme - Render</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
            body { background: #0f172a; color: #f8fafc; line-height: 1.6; padding: 20px; }
            
            .container { max-width: 800px; margin: 0 auto; }
            
            header { text-align: center; margin-bottom: 30px; }
            h1 { font-size: 2.5rem; margin-bottom: 10px; color: #60a5fa; }
            .subtitle { color: #94a3b8; font-size: 1.1rem; }
            
            .status-card { background: #1e293b; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .status-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
            .status-badge { padding: 5px 15px; border-radius: 20px; font-weight: bold; }
            .status-running { background: #10b981; }
            .status-stopped { background: #ef4444; }
            .status-error { background: #f59e0b; }
            
            .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }
            .stat { background: #334155; padding: 15px; border-radius: 8px; text-align: center; }
            .stat-value { font-size: 1.8rem; font-weight: bold; }
            .stat-label { color: #94a3b8; font-size: 0.9rem; }
            
            .controls { display: flex; gap: 10px; margin: 20px 0; }
            .btn { padding: 12px 24px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; transition: 0.2s; }
            .btn:hover { opacity: 0.9; transform: translateY(-2px); }
            .btn-start { background: #10b981; color: white; }
            .btn-stop { background: #ef4444; color: white; }
            .btn-refresh { background: #3b82f6; color: white; }
            
            .log-container { background: #1e293b; padding: 15px; border-radius: 10px; margin-top: 20px; }
            .logs { height: 200px; overflow-y: auto; background: #0f172a; padding: 10px; border-radius: 5px; font-family: monospace; font-size: 0.9rem; }
            .log-entry { padding: 5px 0; border-bottom: 1px solid #334155; }
            
            footer { text-align: center; margin-top: 30px; color: #64748b; font-size: 0.9rem; }
            
            @media (max-width: 600px) {
                .controls { flex-direction: column; }
                .stats-grid { grid-template-columns: 1fr; }
            }
        </style>
        <script>
            async function updateStatus() {
                try {
                    const response = await fetch('/api/status');
                    const data = await response.json();
                    
                    // Update status
                    document.getElementById('bot-state').textContent = data.state.toUpperCase();
                    document.getElementById('bot-state').className = 'status-badge status-' + data.state;
                    
                    // Update metrics
                    document.getElementById('total-checks').textContent = data.metrics.total_checks;
                    document.getElementById('success-rate').textContent = data.success_rate.toFixed(1) + '%';
                    document.getElementById('uptime').textContent = data.uptime;
                    document.getElementById('driver-status').textContent = data.driver_active ? '✅ Active' : '❌ Inactive';
                    
                    // Update control buttons
                    const startBtn = document.getElementById('start-btn');
                    const stopBtn = document.getElementById('stop-btn');
                    
                    if (data.state === 'running') {
                        startBtn.disabled = true;
                        stopBtn.disabled = false;
                    } else {
                        startBtn.disabled = false;
                        stopBtn.disabled = true;
                    }
                    
                } catch (error) {
                    console.error('Failed to update status:', error);
                }
            }
            
            async function sendCommand(command) {
                try {
                    const response = await fetch('/api/' + command, { method: 'POST' });
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        alert('✅ Command executed: ' + command);
                        setTimeout(updateStatus, 1000);
                    } else {
                        alert('❌ Error: ' + result.message);
                    }
                } catch (error) {
                    alert('❌ Failed to send command: ' + error);
                }
            }
            
            // Auto-refresh every 5 seconds
            setInterval(updateStatus, 5000);
            window.onload = updateStatus;
        </script>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🤖 Colab Supreme</h1>
                <div class="subtitle">Render.com Edition • 24/7 Colab Protection</div>
            </header>
            
            <div class="status-card">
                <div class="status-header">
                    <h2>Bot Status</h2>
                    <div id="bot-state" class="status-badge">Loading...</div>
                </div>
                
                <div class="stats-grid">
                    <div class="stat">
                        <div class="stat-value" id="total-checks">0</div>
                        <div class="stat-label">Total Checks</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" id="success-rate">0%</div>
                        <div class="stat-label">Success Rate</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" id="uptime">0:00</div>
                        <div class="stat-label">Uptime</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" id="driver-status">❓</div>
                        <div class="stat-label">Driver</div>
                    </div>
                </div>
                
                <div class="controls">
                    <button id="start-btn" class="btn btn-start" onclick="sendCommand('start')">▶️ Start Bot</button>
                    <button id="stop-btn" class="btn btn-stop" onclick="sendCommand('stop')" disabled>⏹️ Stop Bot</button>
                    <button class="btn btn-refresh" onclick="updateStatus()">🔄 Refresh</button>
                </div>
            </div>
            
            <div class="log-container">
                <h3>Recent Activity</h3>
                <div class="logs" id="logs">
                    <div class="log-entry">🚀 Dashboard loaded. Bot status will update automatically.</div>
                    <div class="log-entry">⏳ Waiting for first status update...</div>
                </div>
            </div>
            
            <footer>
                <p>🤖 Colab Supreme v3.1.0 • Optimized for Render.com • Free Tier Compatible</p>
                <p>⚠️ Educational use only • Monitor your Render usage hours</p>
            </footer>
        </div>
    </body>
    </html>
    '''
    
    return html

@app.route('/health')
def health():
    """Health check endpoint for Render"""
    try:
        status = {
            "status": "healthy",
            "bot_state": bot.state,
            "timestamp": datetime.now().isoformat(),
            "memory_mb": psutil.Process().memory_info().rss / 1024 / 1024
        }
        return jsonify(status)
    except:
        return jsonify({"status": "error"}), 500

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify(bot.get_status())

@app.route('/api/start', methods=['POST'])
def api_start():
    """Start bot API"""
    try:
        success = bot.start()
        if success:
            return jsonify({"status": "success", "message": "Bot started"})
        else:
            return jsonify({"status": "error", "message": "Failed to start bot"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/stop', methods=['POST'])
def api_stop():
    """Stop bot API"""
    try:
        success = bot.stop()
        if success:
            return jsonify({"status": "success", "message": "Bot stopped"})
        else:
            return jsonify({"status": "error", "message": "Failed to stop bot"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), mimetype='text/plain')

# ==================== MAIN ====================

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"⚠️ Received signal {signum}, shutting down...")
    bot.stop()
    sys.exit(0)

def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("🚀 AI COLAB SUPREME - RENDER.COM EDITION")
    logger.info("=" * 60)
    logger.info(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"🌐 Colab URL: {Config.get('COLAB_URL')}")
    logger.info(f"🖥️  Selenium: {'✅ Available' if SELENIUM_AVAILABLE else '❌ Not available'}")
    logger.info(f"🤖 AI: {'✅ Available' if AI_AVAILABLE else '❌ Not available'}")
    logger.info(f"⚙️  Check Interval: {Config.get('CHECK_INTERVAL')}s")
    logger.info("=" * 60)
    
    # Setup Chrome if on Render
    if Config.get("RENDER"):
        setup_chrome()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Auto-start bot if configured
    if Config.get("AUTO_START") and SELENIUM_AVAILABLE:
        logger.info("🔄 Auto-starting bot...")
        bot.start()
    
    # Start Flask app
    port = Config.get("PORT")
    logger.info(f"🌐 Web dashboard: http://localhost:{port}")
    logger.info(f"🏥 Health check: http://localhost:{port}/health")
    logger.info(f"📊 Metrics: http://localhost:{port}/metrics")
    logger.info("=" * 60)
    
    # Run Flask
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    main()
