#!/usr/bin/env python3
"""
🔥 ULTIMATE COLAB KEEPER BOT v4.0
✅ 24/7 Colab Runtime Keeper
✅ Human-Like Behavior Simulation
✅ Auto-Recovery All Failures
✅ UptimeRobot Compatible
✅ Render.com Ready
✅ Multiple Colab Support
✅ Telegram/Discord Alerts
✅ Advanced Anti-Detection
✅ Smart Resource Management
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
from dataclasses import dataclass, asdict
from enum import Enum
from urllib.parse import urlparse

# Flask for web server (Render.com compatibility)
try:
    from flask import Flask, jsonify, request, render_template_string
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("Warning: Flask not installed, web dashboard disabled")

# Selenium for browser automation
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("Warning: Selenium not installed, browser automation disabled")

# Additional imports
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# ============================================================================
# CONFIGURATION
# ============================================================================

class BotMode(Enum):
    """Bot operation modes"""
    AGGRESSIVE = "aggressive"      # Max uptime, higher detection risk
    BALANCED = "balanced"          # Recommended (default)
    STEALTH = "stealth"            # Mimic human perfectly, slower recovery
    TURBO = "turbo"                # For short-term heavy workloads

@dataclass
class ColabConfig:
    """Individual Colab notebook configuration"""
    name: str
    url: str
    priority: int = 1
    auto_run_cells: bool = True
    preserve_outputs: bool = False
    check_interval: int = 120  # seconds

@dataclass
class HumanProfile:
    """Human behavior profile"""
    typing_speed: Tuple[float, float] = (0.08, 0.25)  # seconds per char
    mouse_speed: Tuple[float, float] = (0.3, 1.2)     # seconds per action
    attention_span: Tuple[int, int] = (300, 1200)     # seconds between breaks
    break_duration: Tuple[int, int] = (30, 300)       # seconds break length
    error_rate: float = 0.02                          # % of typos/clicks

@dataclass
class NotificationConfig:
    """Alert configuration"""
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    discord_webhook: str = ""
    email: str = ""
    alert_on_disconnect: bool = True
    alert_on_error: bool = True
    alert_on_restart: bool = True

# ============================================================================
# LOGGING SETUP
# ============================================================================

class ColoredFormatter(logging.Formatter):
    """Colorful logging output"""
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[41m',   # Red background
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        message = super().format(record)
        return f"{log_color}{message}{self.RESET}"

# Setup logger
logger = logging.getLogger('ColabKeeper')
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(ColoredFormatter(
    '%(asctime)s | %(levelname)8s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))
logger.addHandler(console_handler)

# File handler (optional)
try:
    file_handler = logging.FileHandler('colab_keeper.log')
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s | %(levelname)8s | %(name)s | %(message)s'
    ))
    logger.addHandler(file_handler)
except:
    pass

# ============================================================================
# MAIN BOT CLASS
# ============================================================================

class UltimateColabKeeper:
    """Ultimate Colab Keeper Bot with all features"""
    
    VERSION = "4.0.0"
    
    def __init__(self):
        # Core configuration
        self.mode = BotMode(os.getenv("BOT_MODE", "balanced"))
        self.colabs: List[ColabConfig] = []
        self.human_profile = HumanProfile()
        self.notifications = NotificationConfig()
        
        # State tracking
        self.status = {
            "start_time": datetime.now(),
            "total_uptime": timedelta(0),
            "restart_count": 0,
            "error_count": 0,
            "successful_checks": 0,
            "last_check": None,
            "current_colab": None,
            "is_running": False
        }
        
        # Browser instance
        self.driver = None
        self.browser_healthy = False
        
        # Thread management
        self.monitor_thread = None
        self.keepalive_thread = None
        self.health_thread = None
        
        # Resource tracking
        self.resource_usage = {
            "cpu": [],
            "memory": [],
            "network": []
        }
        
        # Load configuration
        self._load_config()
        
        logger.info(f"Ultimate Colab Keeper v{self.VERSION} initialized")
        logger.info(f"Mode: {self.mode.value}")
    
    def _load_config(self):
        """Load configuration from environment and files"""
        
        # Load Colab URLs (comma separated)
        colab_urls = os.getenv("COLAB_URLS", "").split(",")
        for i, url in enumerate(colab_urls):
            url = url.strip()
            if url and url.startswith("http"):
                self.colabs.append(ColabConfig(
                    name=f"Colab-{i+1}",
                    url=url,
                    priority=i+1
                ))
        
        # If no URLs in env, check for single URL
        if not self.colabs:
            single_url = os.getenv("COLAB_URL")
            if single_url:
                self.colabs.append(ColabConfig(
                    name="Primary-Colab",
                    url=single_url,
                    priority=1
                ))
        
        # Load notification config
        self.notifications.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.notifications.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
        self.notifications.discord_webhook = os.getenv("DISCORD_WEBHOOK", "")
        self.notifications.email = os.getenv("ALERT_EMAIL", "")
    
    # ========================================================================
    # HUMAN BEHAVIOR SIMULATION
    # ========================================================================
    
    def human_delay(self, action_type: str = "thinking"):
        """Random delay based on action type and human profile"""
        
        delay_presets = {
            "typing": self.human_profile.typing_speed,
            "clicking": (0.2, 0.8),
            "thinking": (0.5, 3.0),
            "reading": (1.0, 5.0),
            "waiting": (3.0, 10.0),
        }
        
        if action_type in delay_presets:
            min_delay, max_delay = delay_presets[action_type]
        else:
            min_delay, max_delay = 0.5, 2.0
        
        # Add randomness
        delay = random.uniform(min_delay, max_delay)
        
        # Mode adjustments
        if self.mode == BotMode.TURBO:
            delay *= 0.3
        elif self.mode == BotMode.STEALTH:
            delay *= 1.5
        
        time.sleep(delay)
        return delay
    
    def human_type(self, element, text: str):
        """Type text like a human with occasional mistakes"""
        try:
            self.human_delay("clicking")
            element.click()
            
            for char in text:
                # Simulate typing speed variations
                type_delay = random.uniform(*self.human_profile.typing_speed)
                
                # Occasional typos (based on error rate)
                if random.random() < self.human_profile.error_rate:
                    wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz1234567890')
                    element.send_keys(wrong_char)
                    time.sleep(type_delay * 0.5)
                    element.send_keys(Keys.BACKSPACE)
                    time.sleep(type_delay * 0.3)
                
                # Type correct character
                element.send_keys(char)
                time.sleep(type_delay)
            
            # Final pause before Enter
            self.human_delay("thinking")
            
        except Exception as e:
            logger.warning(f"Human typing failed: {e}")
            element.send_keys(text)
    
    def human_click(self, element):
        """Click element with human-like imperfections"""
        try:
            # Move mouse to element with slight offset
            actions = ActionChains(self.driver)
            
            # Add randomness to mouse movement
            offset_x = random.randint(-10, 10)
            offset_y = random.randint(-10, 10)
            
            actions.move_to_element_with_offset(element, offset_x, offset_y)
            
            # Small pause before click
            actions.pause(random.uniform(0.1, 0.5))
            
            # Click
            actions.click()
            
            # Small pause after click
            actions.pause(random.uniform(0.05, 0.2))
            
            actions.perform()
            self.human_delay("clicking")
            
        except Exception as e:
            logger.warning(f"Human click failed: {e}")
            try:
                element.click()
            except:
                pass
    
    def human_scroll(self, direction: str = "down", amount: int = None):
        """Scroll like a human"""
        if not self.driver:
            return
        
        if amount is None:
            amount = random.randint(200, 800)
        
        if direction == "up":
            amount = -amount
        
        # Split scroll into multiple steps for human-like behavior
        steps = random.randint(2, 5)
        step_size = amount // steps
        
        for i in range(steps):
            # Add slight randomness to each step
            current_step = step_size + random.randint(-50, 50)
            self.driver.execute_script(f"window.scrollBy(0, {current_step});")
            time.sleep(random.uniform(0.05, 0.2))
        
        self.human_delay("reading")
    
    def take_break(self):
        """Simulate human taking a break"""
        if random.random() < 0.3:  # 30% chance of break
            break_time = random.randint(*self.human_profile.break_duration)
            logger.info(f"🤖 Taking human-like break for {break_time}s")
            time.sleep(break_time)
    
    # ========================================================================
    # BROWSER MANAGEMENT
    # ========================================================================
    
    def setup_browser(self):
        """Setup Chrome browser with anti-detection measures"""
        if not SELENIUM_AVAILABLE:
            logger.error("Selenium not available. Install: pip install selenium undetected-chromedriver")
            return False
        
        try:
            # Try undetected-chromedriver first
            try:
                import undetected_chromedriver as uc
                options = uc.ChromeOptions()
            except ImportError:
                from selenium.webdriver.chrome.options import Options
                options = Options()
                logger.warning("undetected-chromedriver not found, using standard Chrome")
            
            # Anti-detection options
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-gpu")
            
            # Random window size
            width = random.choice([1920, 1366, 1536, 1440, 1280])
            height = random.choice([1080, 768, 864, 900, 720])
            options.add_argument(f"--window-size={width},{height}")
            
            # Random user agent
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]
            options.add_argument(f"user-agent={random.choice(user_agents)}")
            
            # Additional stealth options
            options.add_argument("--disable-web-security")
            options.add_argument("--disable-features=VizDisplayCompositor")
            options.add_argument("--disable-background-timer-throttling")
            options.add_argument("--disable-backgrounding-occluded-windows")
            options.add_argument("--disable-renderer-backgrounding")
            
            # Create driver
            if 'uc' in locals():
                self.driver = uc.Chrome(options=options, headless=False)
            else:
                from selenium.webdriver import Chrome
                self.driver = Chrome(options=options)
            
            # Execute CDP commands for additional stealth
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": self.driver.execute_script("return navigator.userAgent").replace("Headless", "")
            })
            
            self.browser_healthy = True
            logger.info("✅ Browser setup complete with anti-detection measures")
            return True
            
        except Exception as e:
            logger.error(f"❌ Browser setup failed: {e}")
            self.browser_healthy = False
            return False
    
    def save_cookies(self, filename: str = "colab_cookies.json"):
        """Save browser cookies for future sessions"""
        try:
            if self.driver:
                cookies = self.driver.get_cookies()
                with open(filename, 'w') as f:
                    json.dump(cookies, f, indent=2)
                logger.info(f"💾 Cookies saved to {filename}")
                return True
        except Exception as e:
            logger.warning(f"Could not save cookies: {e}")
        return False
    
    def load_cookies(self, filename: str = "colab_cookies.json"):
        """Load saved cookies"""
        try:
            with open(filename, 'r') as f:
                cookies = json.load(f)
            
            if self.driver:
                # Clear existing cookies first
                self.driver.delete_all_cookies()
                
                # Load saved cookies
                for cookie in cookies:
                    try:
                        # Add domain if missing
                        if 'domain' not in cookie:
                            cookie['domain'] = '.google.com'
                        self.driver.add_cookie(cookie)
                    except Exception as e:
                        logger.debug(f"Could not load cookie: {e}")
                
                logger.info(f"📂 Loaded cookies from {filename}")
                return True
        except FileNotFoundError:
            logger.info("No saved cookies found")
        except Exception as e:
            logger.warning(f"Could not load cookies: {e}")
        return False
    
    # ========================================================================
    # COLAB MONITORING & RECOVERY
    # ========================================================================
    
    def detect_colab_state(self) -> Dict[str, bool]:
        """Detect current Colab state"""
        if not self.driver:
            return {"error": True, "message": "Browser not available"}
        
        state = {
            "disconnected": False,
            "idle_timeout": False,
            "cells_stopped": True,
            "resources_exhausted": False,
            "login_required": False,
            "error_present": False
        }
        
        try:
            page_source = self.driver.page_source.lower()
            page_text = self.driver.find_element(By.TAG_NAME, 'body').text.lower()
            
            # Check for disconnection
            disconnect_indicators = [
                "runtime disconnected",
                "connect to runtime",
                "not connected to a runtime",
                "your session crashed",
                "reconnect",
                "runtime has been idle"
            ]
            
            for indicator in disconnect_indicators:
                if indicator in page_source or indicator in page_text:
                    state["disconnected"] = True
                    logger.warning(f"⚠️ Detected: {indicator}")
            
            # Check for running cells
            running_indicators = [
                "stop button",
                "executing code",
                "running for",
                "spinner",
                "fa-spinner"
            ]
            
            for indicator in running_indicators:
                if indicator in page_source:
                    state["cells_stopped"] = False
            
            # Check for errors
            error_indicators = [
                "error occurred",
                "exception",
                "traceback",
                "crashed",
                "failed",
                "out of memory",
                "resource exhausted"
            ]
            
            for indicator in error_indicators:
                if indicator in page_source or indicator in page_text:
                    state["error_present"] = True
                    logger.error(f"❌ Detected error: {indicator}")
            
            # Check for login requirement
            login_indicators = [
                "sign in",
                "accounts.google.com",
                "choose an account"
            ]
            
            for indicator in login_indicators:
                if indicator in page_source or indicator in page_text:
                    state["login_required"] = True
            
            # Check URL
            current_url = self.driver.current_url
            if "accounts.google.com" in current_url:
                state["login_required"] = True
            
        except Exception as e:
            logger.error(f"Error detecting state: {e}")
            state["error"] = True
        
        return state
    
    def recover_colab(self, state: Dict) -> bool:
        """Attempt to recover Colab based on detected state"""
        
        logger.info("🔄 Attempting recovery...")
        
        try:
            # If login required
            if state.get("login_required"):
                return self.handle_login()
            
            # If disconnected
            if state.get("disconnected"):
                return self.reconnect_runtime()
            
            # If cells stopped
            if state.get("cells_stopped"):
                return self.run_cells()
            
            # If error present
            if state.get("error_present"):
                return self.restart_runtime()
            
            # General refresh if unsure
            self.driver.refresh()
            self.human_delay("waiting")
            
            return True
            
        except Exception as e:
            logger.error(f"Recovery failed: {e}")
            return False
    
    def handle_login(self) -> bool:
        """Handle Google login"""
        logger.info("🔐 Handling login...")
        
        try:
            # Check if we're on login page
            if "accounts.google.com" not in self.driver.current_url:
                # Navigate to login
                self.driver.get("https://accounts.google.com")
                self.human_delay("waiting")
            
            # Try to load cookies first
            if self.load_cookies():
                self.driver.refresh()
                self.human_delay("waiting")
                
                # Check if login successful
                if "myaccount.google.com" in self.driver.current_url or "colab.research.google.com" in self.driver.current_url:
                    logger.info("✅ Login via cookies successful")
                    return True
            
            # Manual login (requires credentials in env)
            email = os.getenv("GOOGLE_EMAIL")
            password = os.getenv("GOOGLE_PASSWORD")  # Use App Password!
            
            if not email or not password:
                logger.error("❌ Login credentials not found in environment")
                return False
            
            # Find email field
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "identifierId"))
            )
            
            # Human-like email entry
            self.human_click(email_field)
            self.human_type(email_field, email)
            email_field.send_keys(Keys.RETURN)
            
            self.human_delay("thinking")
            
            # Find password field
            password_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "Passwd"))
            )
            
            # Human-like password entry
            self.human_click(password_field)
            self.human_type(password_field, password)
            password_field.send_keys(Keys.RETURN)
            
            self.human_delay("waiting")
            
            # Save cookies for next time
            self.save_cookies()
            
            logger.info("✅ Manual login successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Login failed: {e}")
            return False
    
    def reconnect_runtime(self) -> bool:
        """Click Connect/Reconnect button"""
        logger.info("🔗 Attempting to reconnect runtime...")
        
        try:
            # Try different button selectors
            button_selectors = [
                "//*[contains(text(), 'Connect')]",
                "//*[contains(text(), 'RECONNECT')]",
                "//button[contains(., 'Connect')]",
                "//button[contains(., 'Reconnect')]",
                "//div[contains(@class, 'connect-button')]",
                "//paper-button[contains(., 'Connect')]"
            ]
            
            for selector in button_selectors:
                try:
                    buttons = self.driver.find_elements(By.XPATH, selector)
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            self.human_click(button)
                            logger.info(f"✅ Clicked connect button: {selector}")
                            self.human_delay("waiting")
                            return True
                except:
                    continue
            
            # If no connect button found, try to run a cell
            return self.run_cells()
            
        except Exception as e:
            logger.error(f"❌ Reconnect failed: {e}")
            return False
    
    def restart_runtime(self) -> bool:
        """Restart the Colab runtime"""
        logger.info("🔄 Restarting runtime...")
        
        try:
            # Click Runtime menu
            runtime_menus = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Runtime')]")
            
            for menu in runtime_menus:
                if menu.is_displayed():
                    self.human_click(menu)
                    self.human_delay("thinking")
                    
                    # Look for restart option
                    restart_options = self.driver.find_elements(
                        By.XPATH, "//*[contains(text(), 'Restart runtime')]"
                    )
                    
                    for option in restart_options:
                        if option.is_displayed():
                            self.human_click(option)
                            self.human_delay("thinking")
                            
                            # Confirm dialog
                            confirm_buttons = self.driver.find_elements(
                                By.XPATH, "//button[contains(., 'Restart') or contains(., 'Yes')]"
                            )
                            
                            for confirm in confirm_buttons:
                                if confirm.is_displayed():
                                    self.human_click(confirm)
                                    logger.info("✅ Runtime restart initiated")
                                    self.human_delay("waiting")
                                    
                                    # Wait for restart
                                    time.sleep(10)
                                    return True
            
            # Fallback: Factory reset runtime
            self.driver.get(self.driver.current_url + "&force=true")
            self.human_delay("waiting")
            logger.info("✅ Runtime reset via URL")
            return True
            
        except Exception as e:
            logger.error(f"❌ Restart failed: {e}")
            return False
    
    def run_cells(self) -> bool:
        """Run all cells in the notebook"""
        logger.info("▶️ Running cells...")
        
        try:
            # Method 1: Runtime -> Run all
            runtime_menus = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Runtime')]")
            
            for menu in runtime_menus:
                if menu.is_displayed():
                    self.human_click(menu)
                    self.human_delay("thinking")
                    
                    # Look for Run all option
                    runall_options = self.driver.find_elements(
                        By.XPATH, "//*[contains(text(), 'Run all')]"
                    )
                    
                    for option in runall_options:
                        if option.is_displayed():
                            self.human_click(option)
                            logger.info("✅ Running all cells")
                            self.human_delay("waiting")
                            return True
            
            # Method 2: Keyboard shortcut
            actions = ActionChains(self.driver)
            actions.key_down(Keys.CONTROL).key_down(Keys.F9).key_up(Keys.F9).key_up(Keys.CONTROL).perform()
            logger.info("✅ Sent Ctrl+F9 to run cells")
            self.human_delay("waiting")
            return True
            
        except Exception as e:
            logger.error(f"❌ Run cells failed: {e}")
            return False
    
    # ========================================================================
    # NOTIFICATION SYSTEM
    # ========================================================================
    
    def send_notification(self, title: str, message: str, level: str = "info"):
        """Send notification via configured channels"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"[{timestamp}] {title}\n{message}"
        
        # Telegram
        if self.notifications.telegram_bot_token and self.notifications.telegram_chat_id:
            try:
                url = f"https://api.telegram.org/bot{self.notifications.telegram_bot_token}/sendMessage"
                payload = {
                    "chat_id": self.notifications.telegram_chat_id,
                    "text": full_message,
                    "parse_mode": "HTML"
                }
                requests.post(url, json=payload, timeout=5)
                logger.info("📱 Telegram notification sent")
            except Exception as e:
                logger.warning(f"Telegram notification failed: {e}")
        
        # Discord
        if self.notifications.discord_webhook:
            try:
                color = {
                    "info": 3447003,      # Blue
                    "warning": 16776960,  # Yellow
                    "error": 16711680,    # Red
                    "success": 65280      # Green
                }.get(level, 3447003)
                
                embed = {
                    "title": title,
                    "description": message,
                    "color": color,
                    "timestamp": datetime.now().isoformat(),
                    "footer": {"text": "Colab Keeper Bot"}
                }
                
                payload = {"embeds": [embed]}
                requests.post(self.notifications.discord_webhook, json=payload, timeout=5)
                logger.info("💬 Discord notification sent")
            except Exception as e:
                logger.warning(f"Discord notification failed: {e}")
    
    # ========================================================================
    # RESOURCE MONITORING
    # ========================================================================
    
    def monitor_resources(self):
        """Monitor system resources"""
        if not PSUTIL_AVAILABLE:
            return
        
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            self.resource_usage["cpu"].append(cpu_percent)
            self.resource_usage["memory"].append(memory.percent)
            
            # Keep last 100 readings
            for key in self.resource_usage:
                if len(self.resource_usage[key]) > 100:
                    self.resource_usage[key] = self.resource_usage[key][-100:]
            
            # Alert if resources high
            if cpu_percent > 80 or memory.percent > 85:
                self.send_notification(
                    "⚠️ High Resource Usage",
                    f"CPU: {cpu_percent}% | Memory: {memory.percent}%",
                    "warning"
                )
                
        except Exception as e:
            logger.debug(f"Resource monitoring error: {e}")
    
    # ========================================================================
    # MAIN MONITORING LOOP
    # ========================================================================
    
    def monitor_loop(self):
        """Main monitoring loop"""
        logger.info("🚀 Starting monitor loop")
        
        check_interval = 120  # Start with 2 minutes
        
        while self.status["is_running"]:
            try:
                self.status["last_check"] = datetime.now()
                
                # Monitor resources
                self.monitor_resources()
                
                # Check each Colab
                for colab in sorted(self.colabs, key=lambda x: x.priority):
                    self.status["current_colab"] = colab.name
                    
                    # Navigate to Colab if not already there
                    if self.driver.current_url != colab.url:
                        logger.info(f"🌐 Navigating to {colab.name}")
                        self.driver.get(colab.url)
                        self.human_delay("waiting")
                    
                    # Detect state
                    state = self.detect_colab_state()
                    
                    # Take action if needed
                    if any(state.values()):
                        logger.info(f"🛠️ {colab.name} needs attention: {state}")
                        
                        if not self.recover_colab(state):
                            logger.error(f"❌ Recovery failed for {colab.name}")
                            self.status["error_count"] += 1
                            
                            # Send alert
                            if self.notifications.alert_on_error:
                                self.send_notification(
                                    "❌ Colab Recovery Failed",
                                    f"Colab: {colab.name}\nState: {state}",
                                    "error"
                                )
                        else:
                            self.status["successful_checks"] += 1
                            logger.info(f"✅ {colab.name} recovered successfully")
                            
                            if self.notifications.alert_on_restart:
                                self.send_notification(
                                    "🔄 Colab Restarted",
                                    f"Colab: {colab.name}\nTime: {datetime.now().strftime('%H:%M:%S')}",
                                    "info"
                                )
                    else:
                        self.status["successful_checks"] += 1
                        logger.debug(f"✅ {colab.name} is healthy")
                    
                    # Reset idle timer with human-like activity
                    self.reset_idle_timer()
                    
                    # Take occasional breaks
                    self.take_break()
                    
                    # Update total uptime
                    self.status["total_uptime"] = datetime.now() - self.status["start_time"]
                
                # Adaptive check interval
                if self.status["error_count"] > 5:
                    check_interval = 30  # Check more often if errors
                elif self.status["successful_checks"] > 20:
                    check_interval = 180  # Check less often if stable
                
                # Wait for next check with jitter
                jitter = random.uniform(0.8, 1.2)
                time.sleep(check_interval * jitter)
                
            except KeyboardInterrupt:
                logger.info("🛑 Monitor loop interrupted by user")
                break
                
            except Exception as e:
                logger.error(f"🔥 Critical error in monitor loop: {e}")
                self.status["error_count"] += 1
                
                # Attempt browser recovery
                try:
                    if self.driver:
                        self.driver.quit()
                except:
                    pass
                
                self.setup_browser()
                time.sleep(10)
    
    def reset_idle_timer(self):
        """Reset Colab idle timer with human-like activity"""
        
        activities = [
            lambda: self.human_scroll("down", random.randint(100, 400)),
            lambda: self.human_scroll("up", random.randint(50, 200)),
            lambda: self.human_delay("reading"),
            lambda: self.click_random_element(),
        ]
        
        # Do 1-3 random activities
        for _ in range(random.randint(1, 3)):
            random.choice(activities)()
    
    def click_random_element(self):
        """Click a random safe element"""
        try:
            safe_elements = [
                "//div[contains(@class, 'cell')]",
                "//div[contains(@class, 'output')]",
                "//div[contains(@class, 'content')]",
                "//div[contains(@class, 'header')]"
            ]
            
            for selector in safe_elements:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        element = random.choice(elements)
                        if element.is_displayed():
                            self.human_click(element)
                            return True
                except:
                    continue
        except:
            pass
        return False
    
    # ========================================================================
    # CONTROL METHODS
    # ========================================================================
    
    def start(self):
        """Start the bot"""
        if self.status["is_running"]:
            logger.warning("Bot is already running")
            return False
        
        logger.info("🚀 Starting Ultimate Colab Keeper Bot")
        
        # Setup browser
        if not self.setup_browser():
            logger.error("❌ Failed to setup browser")
            return False
        
        # Load cookies
        self.load_cookies()
        
        # Start monitoring thread
        self.status["is_running"] = True
        self.status["start_time"] = datetime.now()
        
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        # Start health thread
        self.health_thread = threading.Thread(target=self.health_check_loop, daemon=True)
        self.health_thread.start()
        
        logger.info("✅ Bot started successfully")
        
        # Send startup notification
        self.send_notification(
            "🚀 Colab Keeper Started",
            f"Bot v{self.VERSION} started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Mode: {self.mode.value}\n"
            f"Monitoring {len(self.colabs)} Colab(s)",
            "info"
        )
        
        return True
    
    def stop(self):
        """Stop the bot"""
        logger.info("🛑 Stopping bot...")
        
        self.status["is_running"] = False
        
        # Save cookies
        self.save_cookies()
        
        # Close browser
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        
        # Calculate final stats
        uptime = datetime.now() - self.status["start_time"]
        
        logger.info(f"📊 Final Stats:")
        logger.info(f"   Total Uptime: {uptime}")
        logger.info(f"   Restarts: {self.status['restart_count']}")
        logger.info(f"   Errors: {self.status['error_count']}")
        logger.info(f"   Successful Checks: {self.status['successful_checks']}")
        
        # Send shutdown notification
        self.send_notification(
            "🛑 Colab Keeper Stopped",
            f"Bot stopped after {uptime}\n"
            f"Restarts: {self.status['restart_count']}\n"
            f"Errors: {self.status['error_count']}",
            "info"
        )
        
        return True
    
    def health_check_loop(self):
        """Health check for web server"""
        while self.status["is_running"]:
            time.sleep(30)
            # Keep-alive ping
            if self.driver:
                try:
                    self.driver.execute_script("return document.readyState")
                except:
                    logger.warning("Browser not responding, attempting recovery")
                    self.setup_browser()
    
    # ========================================================================
    # WEB DASHBOARD (for Render.com)
    # ========================================================================
    
    def create_web_dashboard(self):
        """Create Flask web dashboard"""
        if not FLASK_AVAILABLE:
            logger.warning("Flask not available, web dashboard disabled")
            return None
        
        app = Flask(__name__)
        
        @app.route('/')
        def dashboard():
            """Main dashboard"""
            template = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Ultimate Colab Keeper v{{ version }}</title>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background: #0f172a; color: #f8fafc; }
                    .container { max-width: 1200px; margin: 0 auto; }
                    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 15px; margin-bottom: 30px; }
                    .card { background: #1e293b; padding: 25px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); }
                    .status-online { color: #10b981; font-weight: bold; }
                    .status-offline { color: #ef4444; font-weight: bold; }
                    .btn { background: #3b82f6; color: white; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; margin: 5px; }
                    .btn:hover { background: #2563eb; }
                    .btn-stop { background: #ef4444; }
                    .btn-stop:hover { background: #dc2626; }
                    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
                    .stat-box { background: #334155; padding: 20px; border-radius: 10px; text-align: center; }
                    .stat-value { font-size: 2em; font-weight: bold; margin: 10px 0; }
                    .colab-list { list-style: none; padding: 0; }
                    .colab-item { background: #475569; padding: 15px; margin: 10px 0; border-radius: 8px; }
                </style>
                <script>
                    function refreshData() {
                        fetch('/api/status')
                            .then(r => r.json())
                            .then(data => {
                                document.getElementById('status').innerHTML = 
                                    data.is_running ? '<span class="status-online">🟢 RUNNING</span>' : 
                                    '<span class="status-offline">🔴 STOPPED</span>';
                                document.getElementById('uptime').textContent = data.uptime;
                                document.getElementById('restarts').textContent = data.restart_count;
                                document.getElementById('errors').textContent = data.error_count;
                                document.getElementById('checks').textContent = data.successful_checks;
                                document.getElementById('current-colab').textContent = data.current_colab || 'None';
                            });
                    }
                    
                    function control(action) {
                        fetch('/api/' + action)
                            .then(r => r.json())
                            .then(data => {
                                alert(data.message);
                                refreshData();
                            });
                    }
                    
                    // Auto-refresh every 10 seconds
                    setInterval(refreshData, 10000);
                    window.onload = refreshData;
                </script>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🚀 Ultimate Colab Keeper v{{ version }}</h1>
                        <p>24/7 Colab Runtime Management System</p>
                    </div>
                    
                    <div class="card">
                        <h2>System Status: <span id="status">Loading...</span></h2>
                        <div class="stats-grid">
                            <div class="stat-box">
                                <div>Uptime</div>
                                <div class="stat-value" id="uptime">00:00:00</div>
                            </div>
                            <div class="stat-box">
                                <div>Restarts</div>
                                <div class="stat-value" id="restarts">0</div>
                            </div>
                            <div class="stat-box">
                                <div>Errors</div>
                                <div class="stat-value" id="errors">0</div>
                            </div>
                            <div class="stat-box">
                                <div>Checks</div>
                                <div class="stat-value" id="checks">0</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h2>Controls</h2>
                        <button class="btn" onclick="control('start')">▶️ Start Bot</button>
                        <button class="btn btn-stop" onclick="control('stop')">⏹️ Stop Bot</button>
                        <button class="btn" onclick="control('restart')">🔄 Restart Bot</button>
                        <button class="btn" onclick="control('status')">📊 Refresh Status</button>
                    </div>
                    
                    <div class="card">
                        <h2>Current Colab: <span id="current-colab">None</span></h2>
                        <h3>Monitored Colabs:</h3>
                        <ul class="colab-list">
                            {% for colab in colabs %}
                            <li class="colab-item">
                                <strong>{{ colab.name }}</strong> (Priority: {{ colab.priority }})<br>
                                <small>{{ colab.url }}</small>
                            </li>
                            {% endfor %}
                        </ul>
                    </div>
                    
                    <div class="card">
                        <h2>Quick Links</h2>
                        <a href="/api/status" target="_blank"><button class="btn">API Status</button></a>
                        <a href="/health" target="_blank"><button class="btn">Health Check</button></a>
                        <a href="/api/logs" target="_blank"><button class="btn">View Logs</button></a>
                    </div>
                </div>
            </body>
            </html>
            """
            return render_template_string(
                template,
                version=self.VERSION,
                colabs=self.colabs
            )
        
        @app.route('/health')
        def health():
            """Health check endpoint for UptimeRobot"""
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "bot_running": self.status["is_running"],
                "version": self.VERSION
            })
        
        @app.route('/api/status')
        def api_status():
            """API status endpoint"""
            uptime = datetime.now() - self.status["start_time"] if self.status["start_time"] else timedelta(0)
            
            return jsonify({
                "is_running": self.status["is_running"],
                "uptime": str(uptime).split('.')[0],
                "restart_count": self.status["restart_count"],
                "error_count": self.status["error_count"],
                "successful_checks": self.status["successful_checks"],
                "current_colab": self.status["current_colab"],
                "mode": self.mode.value,
                "version": self.VERSION,
                "timestamp": datetime.now().isoformat()
            })
        
        @app.route('/api/start')
        def api_start():
            """Start bot via API"""
            if self.status["is_running"]:
                return jsonify({"message": "Bot is already running"})
            
            success = self.start()
            return jsonify({
                "message": "Bot started" if success else "Failed to start bot",
                "success": success
            })
        
        @app.route('/api/stop')
        def api_stop():
            """Stop bot via API"""
            if not self.status["is_running"]:
                return jsonify({"message": "Bot is not running"})
            
            success = self.stop()
            return jsonify({
                "message": "Bot stopped" if success else "Failed to stop bot",
                "success": success
            })
        
        @app.route('/api/restart')
        def api_restart():
            """Restart bot via API"""
            self.stop()
            time.sleep(2)
            success = self.start()
            return jsonify({
                "message": "Bot restarted" if success else "Failed to restart bot",
                "success": success
            })
        
        @app.route('/api/logs')
        def api_logs():
            """View recent logs"""
            try:
                with open('colab_keeper.log', 'r') as f:
                    logs = f.read().split('\n')[-100:]  # Last 100 lines
                return jsonify({"logs": logs})
            except:
                return jsonify({"logs": ["No log file found"]})
        
        return app
    
    # ========================================================================
    # COMMAND LINE INTERFACE
    # ========================================================================
    
    def cli(self):
        """Command line interface"""
        import argparse
        
        parser = argparse.ArgumentParser(description='Ultimate Colab Keeper Bot')
        parser.add_argument('--start', action='store_true', help='Start the bot')
        parser.add_argument('--stop', action='store_true', help='Stop the bot')
        parser.add_argument('--status', action='store_true', help='Show status')
        parser.add_argument('--mode', choices=['stealth', 'balanced', 'aggressive', 'turbo'],
                          default='balanced', help='Bot mode')
        parser.add_argument('--colab-url', help='Colab notebook URL')
        parser.add_argument('--web', action='store_true', help='Start web dashboard')
        parser.add_argument('--port', type=int, default=8080, help='Web dashboard port')
        
        args = parser.parse_args()
        
        if args.colab_url:
            self.colabs = [ColabConfig(name="CLI-Colab", url=args.colab_url, priority=1)]
        
        self.mode = BotMode(args.mode)
        
        if args.start:
            self.start()
            
            if args.web:
                app = self.create_web_dashboard()
                if app:
                    app.run(host='0.0.0.0', port=args.port)
            else:
                # Keep running
                try:
                    while self.status["is_running"]:
                        time.sleep(1)
                except KeyboardInterrupt:
                    self.stop()
        
        elif args.stop:
            self.stop()
        
        elif args.status:
            uptime = datetime.now() - self.status["start_time"] if self.status["start_time"] else timedelta(0)
            
            print("\n" + "="*60)
            print("ULTIMATE COLAB KEEPER - STATUS")
            print("="*60)
            print(f"Version: {self.VERSION}")
            print(f"Status: {'🟢 RUNNING' if self.status['is_running'] else '🔴 STOPPED'}")
            print(f"Mode: {self.mode.value}")
            print(f"Uptime: {uptime}")
            print(f"Colabs: {len(self.colabs)}")
            print(f"Restarts: {self.status['restart_count']}")
            print(f"Errors: {self.status['error_count']}")
            print(f"Successful Checks: {self.status['successful_checks']}")
            
            if self.colabs:
                print("\nMonitored Colabs:")
                for colab in self.colabs:
                    print(f"  • {colab.name} (Priority: {colab.priority})")
                    print(f"    {colab.url[:80]}...")
            
            print("\n" + "="*60)
        
        elif args.web:
            app = self.create_web_dashboard()
            if app:
                app.run(host='0.0.0.0', port=args.port)
        
        else:
            parser.print_help()

# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    print("\n" + "="*70)
    print("🚀 ULTIMATE COLAB KEEPER BOT v4.0")
    print("="*70)
    print("Features: 24/7 Colab Uptime | Human-Like Behavior | Auto-Recovery")
    print("          Multi-Colab Support | Web Dashboard | Notifications")
    print("="*70)
    
    # Check requirements
    if not SELENIUM_AVAILABLE:
        print("\n⚠️  Selenium not installed. Required for browser automation.")
        print("   Install: pip install selenium undetected-chromedriver")
        print("   Or use web-only mode with --web flag")
    
    bot = UltimateColabKeeper()
    
    # Check if running on Render.com (has RENDER environment)
    if os.getenv("RENDER"):
        print("🌐 Detected Render.com environment")
        print("📊 Starting web dashboard...")
        
        app = bot.create_web_dashboard()
        if app:
            # Start bot in background thread
            import threading
            bot_thread = threading.Thread(target=bot.start, daemon=True)
            bot_thread.start()
            
            # Start Flask app
            port = int(os.getenv("PORT", 10000))
            app.run(host='0.0.0.0', port=port, debug=False)
        else:
            print("❌ Web dashboard unavailable")
            bot.cli()
    else:
        # Run CLI
        bot.cli()

if __name__ == "__main__":
    main()
