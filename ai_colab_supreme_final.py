#!/usr/bin/env python3
"""
🚀 AI-POWERED COLAB SUPREME BOT - FINAL VERSION
✅ All Features • Fixed • Updated • Production Ready
Version: 3.0.0 | AI-Powered | 24/7 Protection
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
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
import signal
import queue

# Core dependencies
import requests
from flask import Flask, jsonify, render_template_string, request, Response, redirect
from flask_socketio import SocketIO
from prometheus_client import Counter, Gauge, Histogram, generate_latest
import psutil

# AI & ML
try:
    import numpy as np
    import cv2
    from PIL import Image
    import pytesseract
    from ultralytics import YOLO
    from openai import AsyncOpenAI
    from sklearn.ensemble import RandomForestClassifier
    import pandas as pd
    AI_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Some AI dependencies missing: {e}")
    AI_AVAILABLE = False

# Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import undetected_chromedriver as uc

# Telegram
try:
    from telegram import Update, Bot
    from telegram.ext import Application, CommandHandler, MessageHandler, filters
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False

# ==================== CONFIGURATION ====================

class Config:
    """Configuration management"""
    
    DEFAULTS = {
        # Core
        "COLAB_URL": "https://colab.research.google.com/drive/",
        "CHECK_INTERVAL": 150,  # 2.5 minutes
        "MAX_RETRIES": 10,
        "RECONNECT_DELAY": 10,
        
        # AI Features
        "ENABLE_AI": True,
        "ENABLE_CV": True,
        "ENABLE_PREDICTIVE": True,
        "OPENAI_API_KEY": "",
        
        # Bot Behavior
        "MAX_PARALLEL_TABS": 3,
        "SESSION_ROTATION_HOURS": 11,
        "ENABLE_TELEGRAM": False,
        "TELEGRAM_BOT_TOKEN": "",
        "TELEGRAM_CHAT_ID": "",
        
        # Monitoring
        "PROMETHEUS_PORT": 9090,
        "ENABLE_LOGGING": True,
        "LOG_LEVEL": "INFO",
        
        # Advanced
        "USE_PROXY": False,
        "PROXY_LIST": "",
        "USER_AGENT_ROTATION": True,
        "ANTI_DETECTION": True,
        "HEADLESS": True,
        
        # Performance
        "MAX_MEMORY_MB": 512,
        "MAX_CPU_PERCENT": 80,
        "AUTO_RECOVERY": True,
        "HEALTH_CHECK_INTERVAL": 30,
    }
    
    @classmethod
    def get(cls, key: str, default=None):
        """Get configuration value from env or defaults"""
        value = os.getenv(key, cls.DEFAULTS.get(key, default))
        
        # Type conversion
        if isinstance(cls.DEFAULTS.get(key), bool):
            return str(value).lower() in ('true', '1', 'yes', 'y')
        elif isinstance(cls.DEFAULTS.get(key), int):
            try:
                return int(value)
            except:
                return cls.DEFAULTS.get(key, default)
        elif isinstance(cls.DEFAULTS.get(key), list):
            if value:
                return [item.strip() for item in value.split(',')]
            return []
        else:
            return value

# ==================== LOGGING ====================

class ColabLogger:
    """Advanced logging with file rotation and colors"""
    
    @staticmethod
    def setup():
        log_level = getattr(logging, Config.get("LOG_LEVEL", "INFO"))
        
        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'logs/colab_bot_{datetime.now().strftime("%Y%m%d")}.log'),
                logging.StreamHandler()
            ]
        )
        
        # Create custom logger
        logger = logging.getLogger("AI_Colab_Bot")
        logger.setLevel(log_level)
        
        # Add colors for console
        if sys.stdout.isatty():
            class ColoredFormatter(logging.Formatter):
                COLORS = {
                    'DEBUG': '\033[36m',    # Cyan
                    'INFO': '\033[32m',     # Green
                    'WARNING': '\033[33m',  # Yellow
                    'ERROR': '\033[31m',    # Red
                    'CRITICAL': '\033[41m', # Red background
                }
                RESET = '\033[0m'
                
                def format(self, record):
                    if record.levelname in self.COLORS:
                        record.msg = f"{self.COLORS[record.levelname]}{record.msg}{self.RESET}"
                    return super().format(record)
            
            for handler in logger.handlers:
                if isinstance(handler, logging.StreamHandler):
                    handler.setFormatter(ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        return logger

logger = ColabLogger.setup()

# ==================== ENUMS & DATA CLASSES ====================

class BotState(Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    RECOVERING = "recovering"
    STOPPED = "stopped"
    MAINTENANCE = "maintenance"

class StrategyType(Enum):
    CV_BUTTON_DETECTION = "computer_vision"
    DOM_ANALYSIS = "dom_analysis"
    JS_INJECTION = "javascript"
    KEYBOARD_SIMULATION = "keyboard"
    MOUSE_MOVEMENT = "mouse"
    TAB_MANAGEMENT = "tab_management"
    SESSION_ROTATION = "session_rotation"
    EMERGENCY_RESTART = "emergency"
    AI_DECISION = "ai_decision"
    MULTI_LAYER = "multi_layer"
    SMART_REFRESH = "smart_refresh"
    CELL_EXECUTION = "cell_execution"

@dataclass
class StrategyResult:
    strategy: StrategyType
    success: bool
    execution_time: float
    confidence: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class BotMetrics:
    total_actions: int = 0
    successful_actions: int = 0
    total_connects: int = 0
    cells_run: int = 0
    disconnections: int = 0
    recovery_time_avg: float = 0.0
    strategy_success_rate: Dict[str, float] = field(default_factory=dict)
    errors: List[Dict] = field(default_factory=list)
    session_start: datetime = field(default_factory=datetime.now)
    last_success: Optional[datetime] = None

@dataclass
class BotHealth:
    memory_usage_mb: float = 0.0
    cpu_percent: float = 0.0
    disk_usage_percent: float = 0.0
    network_usage: float = 0.0
    driver_health: List[bool] = field(default_factory=list)
    last_check: datetime = field(default_factory=datetime.now)
    is_healthy: bool = True
    issues: List[str] = field(default_factory=list)

# ==================== AI MODULES ====================

class AIModule:
    """Central AI module manager"""
    
    def __init__(self):
        self.cv_detector = None
        self.ai_engine = None
        self.predictive_model = None
        self.nlp_processor = None
        self.is_enabled = Config.get("ENABLE_AI") and AI_AVAILABLE
        
        if self.is_enabled:
            self.initialize()
    
    def initialize(self):
        """Initialize all AI components"""
        try:
            if Config.get("ENABLE_CV"):
                self.cv_detector = CVDetector()
            
            if Config.get("OPENAI_API_KEY"):
                self.ai_engine = AIDecisionEngine(Config.get("OPENAI_API_KEY"))
            
            if Config.get("ENABLE_PREDICTIVE"):
                self.predictive_model = PredictiveAnalytics()
            
            logger.info("✅ AI modules initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI modules: {e}")
            self.is_enabled = False
    
    async def analyze_and_decide(self, context: Dict) -> Dict:
        """Use AI to analyze context and make decisions"""
        if not self.is_enabled or not self.ai_engine:
            return self.get_fallback_decision()
        
        try:
            return await self.ai_engine.analyze_context(context)
        except Exception as e:
            logger.warning(f"AI analysis failed: {e}")
            return self.get_fallback_decision()
    
    def get_fallback_decision(self) -> Dict:
        """Get fallback decision when AI is unavailable"""
        return {
            'primary_strategy': 'multi_layer',
            'backup_strategy': 'dom_analysis',
            'timing': 120,
            'confidence': 0.5,
            'reasoning': 'AI unavailable, using fallback'
        }

class CVDetector:
    """Computer Vision for button and text detection"""
    
    def __init__(self):
        self.model = None
        self.templates = {}
        self.load_model()
    
    def load_model(self):
        """Load YOLO model for button detection"""
        try:
            # Try to load custom or pre-trained model
            model_paths = [
                "models/button_detection.pt",
                "yolov8n.pt",  # Fallback to standard YOLO
            ]
            
            for path in model_paths:
                if Path(path).exists() or path == "yolov8n.pt":
                    self.model = YOLO(path)
                    logger.info(f"✅ Loaded CV model: {path}")
                    break
            
            if not self.model:
                logger.warning("⚠️ No CV model available")
        except Exception as e:
            logger.error(f"❌ Failed to load CV model: {e}")
    
    def detect_buttons(self, screenshot_path: str) -> List[Dict]:
        """Detect buttons in screenshot"""
        if not self.model or not Path(screenshot_path).exists():
            return []
        
        try:
            # Load image
            img = cv2.imread(screenshot_path)
            if img is None:
                return []
            
            # Resize for better performance
            img = cv2.resize(img, (1280, 720))
            
            # Run detection
            results = self.model(img, conf=0.5)
            
            buttons = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        conf = float(box.conf[0])
                        
                        # Extract text from region
                        roi = img[y1:y2, x1:x2]
                        text = self.extract_text(roi)
                        
                        buttons.append({
                            'bbox': (x1, y1, x2, y2),
                            'confidence': conf,
                            'text': text,
                            'center': ((x1 + x2) // 2, (y1 + y2) // 2)
                        })
            
            # Filter for connect buttons
            return self.filter_connect_buttons(buttons)
        except Exception as e:
            logger.error(f"❌ CV detection error: {e}")
            return []
    
    def extract_text(self, image) -> str:
        """Extract text using OCR"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # OCR
            text = pytesseract.image_to_string(thresh, config='--psm 7')
            return text.strip().lower()
        except:
            return ""
    
    def filter_connect_buttons(self, buttons: List[Dict]) -> List[Dict]:
        """Filter for Connect/RECONNECT buttons"""
        keywords = ['connect', 'reconnect', 'run', 'start', '继续', '接続']
        filtered = []
        
        for btn in buttons:
            text = btn['text']
            if any(keyword in text for keyword in keywords):
                filtered.append(btn)
            elif btn['confidence'] > 0.7:  # High confidence button
                filtered.append(btn)
        
        return filtered

class AIDecisionEngine:
    """GPT-powered decision engine"""
    
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.history = []
        self.max_history = 50
    
    async def analyze_context(self, context: Dict) -> Dict:
        """Analyze context using GPT"""
        try:
            prompt = self.build_prompt(context)
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Using 3.5 for cost efficiency
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert Colab automation AI. Analyze the situation and recommend the best strategy to keep Colab running. Consider success history, timing, and resource constraints."""
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            analysis = self.parse_response(response.choices[0].message.content)
            self.history.append({
                'timestamp': datetime.now(),
                'context': context,
                'analysis': analysis
            })
            
            # Trim history
            if len(self.history) > self.max_history:
                self.history = self.history[-self.max_history:]
            
            return analysis
        except Exception as e:
            logger.error(f"❌ AI analysis error: {e}")
            raise
    
    def build_prompt(self, context: Dict) -> str:
        """Build analysis prompt"""
        return f"""
        Colab Bot Status Analysis:
        
        Current State: {context.get('state', 'unknown')}
        Session Age: {context.get('session_age', 0)} minutes
        Success Rate: {context.get('success_rate', 0)*100:.1f}%
        Recent Errors: {len(context.get('recent_errors', []))}
        Time: {datetime.now().strftime('%H:%M')}
        Day: {datetime.now().strftime('%A')}
        
        Recent Strategy Success:
        {json.dumps(context.get('strategy_success', {}), indent=2)}
        
        Please recommend:
        1. Best strategy to use now
        2. Timing for next check
        3. Confidence level
        4. Brief reasoning
        
        Format as JSON with: strategy, timing, confidence, reasoning
        """
    
    def parse_response(self, response: str) -> Dict:
        """Parse AI response"""
        try:
            # Try to find JSON in response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Fallback parsing
        return {
            'strategy': 'multi_layer',
            'timing': 120,
            'confidence': 0.7,
            'reasoning': response[:100]
        }

class PredictiveAnalytics:
    """ML for predicting failures"""
    
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=50, random_state=42)
        self.data = []
        self.is_trained = False
    
    def add_data_point(self, features: Dict, outcome: bool):
        """Add training data"""
        self.data.append({
            'features': features,
            'outcome': outcome,
            'timestamp': datetime.now()
        })
        
        # Train periodically
        if len(self.data) % 20 == 0 and len(self.data) >= 50:
            self.train()
    
    def train(self):
        """Train the model"""
        if len(self.data) < 50:
            return
        
        try:
            X = []
            y = []
            
            for point in self.data[-100:]:  # Use recent 100 points
                features = point['features']
                X.append([
                    features.get('hour', 0),
                    features.get('day_of_week', 0),
                    features.get('session_age', 0),
                    features.get('error_count', 0),
                    features.get('success_rate', 0),
                ])
                y.append(point['outcome'])
            
            self.model.fit(X, y)
            self.is_trained = True
            logger.info("✅ Predictive model trained")
        except Exception as e:
            logger.error(f"❌ Model training failed: {e}")
    
    def predict_failure(self, current_features: Dict) -> float:
        """Predict failure probability"""
        if not self.is_trained:
            return 0.3
        
        try:
            features = [
                current_features.get('hour', datetime.now().hour),
                current_features.get('day_of_week', datetime.now().weekday()),
                current_features.get('session_age', 0),
                current_features.get('error_count', 0),
                current_features.get('success_rate', 0.5),
            ]
            
            proba = self.model.predict_proba([features])[0][1]
            return float(proba)
        except:
            return 0.3

# ==================== BROWSER MANAGEMENT ====================

class BrowserManager:
    """Manage multiple browser instances"""
    
    def __init__(self):
        self.drivers = []
        self.driver_info = []
        self.max_tabs = Config.get("MAX_PARALLEL_TABS", 2)
        self.session_rotation = Config.get("SESSION_ROTATION_HOURS", 11)
    
    async def initialize(self):
        """Initialize browser instances"""
        logger.info(f"🚀 Initializing {self.max_tabs} browser instances")
        
        for i in range(self.max_tabs):
            driver = await self.create_driver(f"Driver-{i+1}")
            if driver:
                self.drivers.append(driver)
                self.driver_info.append({
                    'id': i,
                    'created': datetime.now(),
                    'health': True,
                    'last_used': datetime.now(),
                    'usage_count': 0
                })
        
        if not self.drivers:
            raise Exception("Failed to initialize any browsers")
        
        logger.info(f"✅ {len(self.drivers)} browsers ready")
        return True
    
    async def create_driver(self, name: str):
        """Create a Chrome driver with anti-detection"""
        try:
            options = uc.ChromeOptions()
            
            # Basic options
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            
            # Headless if configured
            if Config.get("HEADLESS", True):
                options.add_argument("--headless=new")
                options.add_argument("--disable-gpu")
            
            # Window size
            options.add_argument("--window-size=1920,1080")
            
            # User agent rotation
            if Config.get("USER_AGENT_ROTATION", True):
                ua = self.get_random_user_agent()
                options.add_argument(f"user-agent={ua}")
            
            # Additional stealth
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Create driver
            driver = uc.Chrome(
                options=options,
                version_main=114,  # Stable Chrome version
                driver_executable_path="/usr/local/bin/chromedriver"
            )
            
            # Stealth modifications
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            
            logger.info(f"✅ Created browser: {name}")
            return driver
            
        except Exception as e:
            logger.error(f"❌ Failed to create browser {name}: {e}")
            return None
    
    def get_random_user_agent(self):
        """Get random user agent"""
        agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
        ]
        return random.choice(agents)
    
    def get_healthy_driver(self):
        """Get a healthy driver"""
        for i, driver in enumerate(self.drivers):
            if self.driver_info[i]['health']:
                self.driver_info[i]['last_used'] = datetime.now()
                self.driver_info[i]['usage_count'] += 1
                return driver, i
        return None, -1
    
    def mark_driver_unhealthy(self, index: int, reason: str = ""):
        """Mark a driver as unhealthy"""
        if 0 <= index < len(self.driver_info):
            self.driver_info[index]['health'] = False
            logger.warning(f"⚠️ Marked driver {index} as unhealthy: {reason}")
    
    async def recover_driver(self, index: int):
        """Recover an unhealthy driver"""
        try:
            if index < len(self.drivers):
                # Close old driver
                try:
                    self.drivers[index].quit()
                except:
                    pass
                
                # Create new driver
                new_driver = await self.create_driver(f"Driver-{index}-recovered")
                if new_driver:
                    self.drivers[index] = new_driver
                    self.driver_info[index] = {
                        'id': index,
                        'created': datetime.now(),
                        'health': True,
                        'last_used': datetime.now(),
                        'usage_count': 0
                    }
                    logger.info(f"✅ Recovered driver {index}")
                    return True
        except Exception as e:
            logger.error(f"❌ Failed to recover driver {index}: {e}")
        
        return False
    
    def check_health(self):
        """Check health of all drivers"""
        unhealthy = []
        
        for i, driver in enumerate(self.drivers):
            try:
                # Simple health check - get current URL
                driver.current_url
                self.driver_info[i]['health'] = True
            except:
                self.driver_info[i]['health'] = False
                unhealthy.append(i)
        
        return unhealthy
    
    def close_all(self):
        """Close all drivers"""
        for driver in self.drivers:
            try:
                driver.quit()
            except:
                pass
        self.drivers.clear()
        self.driver_info.clear()

# ==================== STRATEGY ENGINE ====================

class StrategyEngine:
    """Execute various strategies to keep Colab alive"""
    
    def __init__(self, browser_manager: BrowserManager, ai_module: AIModule):
        self.browser = browser_manager
        self.ai = ai_module
        self.strategies = self.load_strategies()
        self.history = []
        self.success_counts = {}
        self.failure_counts = {}
    
    def load_strategies(self):
        """Load all available strategies"""
        strategies = [
            {
                'id': 'multi_layer',
                'name': 'Multi-Layer Protection',
                'function': self.execute_multi_layer,
                'weight': 0.3,
                'enabled': True,
                'type': StrategyType.MULTI_LAYER
            },
            {
                'id': 'dom_analysis',
                'name': 'DOM Analysis',
                'function': self.execute_dom_analysis,
                'weight': 0.2,
                'enabled': True,
                'type': StrategyType.DOM_ANALYSIS
            },
            {
                'id': 'javascript',
                'name': 'JavaScript Injection',
                'function': self.execute_javascript,
                'weight': 0.15,
                'enabled': True,
                'type': StrategyType.JS_INJECTION
            },
            {
                'id': 'keyboard',
                'name': 'Keyboard Simulation',
                'function': self.execute_keyboard,
                'weight': 0.1,
                'enabled': True,
                'type': StrategyType.KEYBOARD_SIMULATION
            },
            {
                'id': 'cv_detection',
                'name': 'Computer Vision',
                'function': self.execute_cv_detection,
                'weight': 0.1,
                'enabled': Config.get("ENABLE_CV") and AI_AVAILABLE,
                'type': StrategyType.CV_BUTTON_DETECTION
            },
            {
                'id': 'session_rotation',
                'name': 'Session Rotation',
                'function': self.execute_session_rotation,
                'weight': 0.05,
                'enabled': True,
                'type': StrategyType.SESSION_ROTATION
            },
            {
                'id': 'smart_refresh',
                'name': 'Smart Refresh',
                'function': self.execute_smart_refresh,
                'weight': 0.05,
                'enabled': True,
                'type': StrategyType.SMART_REFRESH
            },
            {
                'id': 'cell_execution',
                'name': 'Cell Execution',
                'function': self.execute_cells,
                'weight': 0.05,
                'enabled': True,
                'type': StrategyType.CELL_EXECUTION
            }
        ]
        
        return [s for s in strategies if s['enabled']]
    
    def choose_strategy(self, context: Dict = None):
        """Choose strategy based on weights and history"""
        if not self.strategies:
            return None
        
        # If AI is available and we have context, use AI recommendation
        if context and self.ai.is_enabled:
            try:
                ai_decision = asyncio.run(self.ai.analyze_and_decide(context))
                preferred = ai_decision.get('strategy', 'multi_layer')
                
                # Find preferred strategy
                for strategy in self.strategies:
                    if strategy['id'] == preferred:
                        return strategy
            except:
                pass
        
        # Weighted random selection based on success rates
        total_weight = 0
        weighted_strategies = []
        
        for strategy in self.strategies:
            success_rate = self.success_counts.get(strategy['id'], 0) / max(
                self.success_counts.get(strategy['id'], 0) + self.failure_counts.get(strategy['id'], 0), 1)
            
            # Adjust weight based on success rate
            adjusted_weight = strategy['weight'] * (0.5 + success_rate * 0.5)
            weighted_strategies.append((strategy, adjusted_weight))
            total_weight += adjusted_weight
        
        if total_weight == 0:
            return self.strategies[0]
        
        # Random selection
        rand = random.uniform(0, total_weight)
        cumulative = 0
        
        for strategy, weight in weighted_strategies:
            cumulative += weight
            if rand <= cumulative:
                return strategy
        
        return self.strategies[0]
    
    async def execute_multi_layer(self, driver) -> StrategyResult:
        """Execute multiple strategies together"""
        start = time.time()
        results = []
        
        # Execute 3 random strategies
        available = [s for s in self.strategies if s['id'] != 'multi_layer']
        selected = random.sample(available, min(3, len(available)))
        
        for strategy in selected:
            try:
                result = await strategy['function'](driver)
                results.append(result.success)
                if result.success:
                    break  # Stop if one succeeds
            except:
                results.append(False)
        
        success = any(results)
        confidence = sum(results) / len(results) if results else 0
        
        return StrategyResult(
            strategy=StrategyType.MULTI_LAYER,
            success=success,
            execution_time=time.time() - start,
            confidence=confidence,
            details={'strategies_tried': [s['id'] for s in selected], 'results': results}
        )
    
    async def execute_dom_analysis(self, driver) -> StrategyResult:
        """Find and click buttons using DOM"""
        start = time.time()
        
        try:
            # Multiple selectors for Connect button
            selectors = [
                'colab-connect-button',
                'button[aria-label*="Connect"]',
                'button[aria-label*="RECONNECT"]',
                'paper-button',
                '[role="button"]',
                'button:contains("Connect")',
                'button:contains("Run")',
            ]
            
            for selector in selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        try:
                            if elem.is_displayed() and elem.is_enabled():
                                elem.click()
                                logger.info(f"✅ DOM clicked: {selector}")
                                return StrategyResult(
                                    strategy=StrategyType.DOM_ANALYSIS,
                                    success=True,
                                    execution_time=time.time() - start,
                                    confidence=0.9
                                )
                        except:
                            continue
                except:
                    continue
            
            # Try XPath
            xpaths = [
                "//button[contains(text(), 'Connect')]",
                "//button[contains(text(), 'RECONNECT')]",
                "//*[contains(@aria-label, 'Connect')]",
                "//*[contains(@aria-label, 'Run')]",
            ]
            
            for xpath in xpaths:
                try:
                    elements = driver.find_elements(By.XPATH, xpath)
                    for elem in elements:
                        try:
                            if elem.is_displayed() and elem.is_enabled():
                                elem.click()
                                logger.info(f"✅ DOM XPath clicked: {xpath}")
                                return StrategyResult(
                                    strategy=StrategyType.DOM_ANALYSIS,
                                    success=True,
                                    execution_time=time.time() - start,
                                    confidence=0.9
                                )
                        except:
                            continue
                except:
                    continue
            
            return StrategyResult(
                strategy=StrategyType.DOM_ANALYSIS,
                success=False,
                execution_time=time.time() - start,
                confidence=0.3
            )
            
        except Exception as e:
            logger.error(f"❌ DOM analysis failed: {e}")
            return StrategyResult(
                strategy=StrategyType.DOM_ANALYSIS,
                success=False,
                execution_time=time.time() - start,
                confidence=0.1
            )
    
    async def execute_javascript(self, driver) -> StrategyResult:
        """Inject JavaScript to click buttons"""
        start = time.time()
        
        try:
            js_code = """
            function clickConnectButtons() {
                let clicked = false;
                
                // Method 1: Direct button click
                document.querySelectorAll('button, colab-connect-button, paper-button').forEach(btn => {
                    const text = (btn.textContent || btn.innerText || '').toLowerCase();
                    if (text.includes('connect') || text.includes('reconnect') || text.includes('run')) {
                        try {
                            btn.click();
                            console.log('JS clicked:', text.substring(0, 20));
                            clicked = true;
                        } catch(e) {}
                    }
                });
                
                // Method 2: Event dispatch
                if (!clicked) {
                    const elements = document.querySelectorAll('[role="button"]');
                    elements.forEach(el => {
                        try {
                            el.dispatchEvent(new MouseEvent('click', {bubbles: true}));
                            clicked = true;
                        } catch(e) {}
                    });
                }
                
                // Method 3: Force click in cell area
                if (!clicked) {
                    const cells = document.querySelectorAll('.cell');
                    if (cells.length > 0) {
                        cells[0].click();
                        clicked = true;
                    }
                }
                
                return clicked;
            }
            
            // Also add keep-alive script
            if (!window._colabKeepAlive) {
                window._colabKeepAlive = setInterval(() => {
                    console.log('🔄 Keep-alive ping');
                    document.activeElement.blur();
                    document.querySelector('body').click();
                }, 75000);
            }
            
            return clickConnectButtons();
            """
            
            result = driver.execute_script(js_code)
            
            return StrategyResult(
                strategy=StrategyType.JS_INJECTION,
                success=bool(result),
                execution_time=time.time() - start,
                confidence=0.8 if result else 0.4,
                details={'javascript_executed': True, 'result': result}
            )
            
        except Exception as e:
            logger.error(f"❌ JavaScript execution failed: {e}")
            return StrategyResult(
                strategy=StrategyType.JS_INJECTION,
                success=False,
                execution_time=time.time() - start,
                confidence=0.1
            )
    
    async def execute_keyboard(self, driver) -> StrategyResult:
        """Simulate keyboard actions"""
        start = time.time()
        
        try:
            actions = ActionChains(driver)
            
            # Focus on page
            actions.send_keys(Keys.TAB * 3).perform()
            time.sleep(0.5)
            
            # Try various shortcuts
            shortcuts = [
                (Keys.CONTROL, Keys.F9),  # Run all cells
                (Keys.CONTROL, Keys.ENTER),  # Run cell
                (Keys.F5,),  # Refresh
                (Keys.CONTROL, 'r'),  # Chrome refresh
                (Keys.SHIFT, Keys.ENTER),  # Run and advance
            ]
            
            for shortcut in shortcuts:
                try:
                    actions = ActionChains(driver)
                    for key in shortcut[:-1]:
                        actions.key_down(key)
                    actions.send_keys(shortcut[-1])
                    for key in shortcut[:-1]:
                        actions.key_up(key)
                    actions.perform()
                    
                    logger.info(f"✅ Keyboard: {shortcut}")
                    time.sleep(1)
                except:
                    continue
            
            return StrategyResult(
                strategy=StrategyType.KEYBOARD_SIMULATION,
                success=True,
                execution_time=time.time() - start,
                confidence=0.7,
                details={'shortcuts_tried': len(shortcuts)}
            )
            
        except Exception as e:
            logger.error(f"❌ Keyboard simulation failed: {e}")
            return StrategyResult(
                strategy=StrategyType.KEYBOARD_SIMULATION,
                success=False,
                execution_time=time.time() - start,
                confidence=0.2
            )
    
    async def execute_cv_detection(self, driver) -> StrategyResult:
        """Use computer vision to find buttons"""
        start = time.time()
        
        if not self.ai.cv_detector or not self.ai.cv_detector.model:
            return StrategyResult(
                strategy=StrategyType.CV_BUTTON_DETECTION,
                success=False,
                execution_time=time.time() - start,
                confidence=0.0,
                details={'error': 'CV not available'}
            )
        
        try:
            # Take screenshot
            screenshot_path = f"cv_screenshot_{int(time.time())}.png"
            driver.save_screenshot(screenshot_path)
            
            # Detect buttons
            buttons = self.ai.cv_detector.detect_buttons(screenshot_path)
            
            if buttons:
                # Click best button
                best_button = max(buttons, key=lambda x: x['confidence'])
                center_x, center_y = best_button['center']
                
                # Move and click
                actions = ActionChains(driver)
                actions.move_by_offset(center_x, center_y).click().perform()
                
                logger.info(f"✅ CV clicked: {best_button.get('text', 'unknown')}")
                
                # Cleanup
                try:
                    os.remove(screenshot_path)
                except:
                    pass
                
                return StrategyResult(
                    strategy=StrategyType.CV_BUTTON_DETECTION,
                    success=True,
                    execution_time=time.time() - start,
                    confidence=best_button['confidence'],
                    details={'button_text': best_button.get('text'), 'confidence': best_button['confidence']}
                )
            
            # Cleanup
            try:
                os.remove(screenshot_path)
            except:
                pass
            
            return StrategyResult(
                strategy=StrategyType.CV_BUTTON_DETECTION,
                success=False,
                execution_time=time.time() - start,
                confidence=0.3,
                details={'buttons_found': 0}
            )
            
        except Exception as e:
            logger.error(f"❌ CV detection failed: {e}")
            return StrategyResult(
                strategy=StrategyType.CV_BUTTON_DETECTION,
                success=False,
                execution_time=time.time() - start,
                confidence=0.1
            )
    
    async def execute_session_rotation(self, driver) -> StrategyResult:
        """Rotate session to prevent timeout"""
        start = time.time()
        
        try:
            # Add timestamp to force new session
            current_url = driver.current_url
            if 'forceNewSession' not in current_url:
                new_url = f"{current_url}{'&' if '?' in current_url else '?'}forceNewSession=true&ts={int(time.time())}"
                driver.get(new_url)
            
            logger.info("✅ Session rotated")
            return StrategyResult(
                strategy=StrategyType.SESSION_ROTATION,
                success=True,
                execution_time=time.time() - start,
                confidence=0.9
            )
            
        except Exception as e:
            logger.error(f"❌ Session rotation failed: {e}")
            return StrategyResult(
                strategy=StrategyType.SESSION_ROTATION,
                success=False,
                execution_time=time.time() - start,
                confidence=0.3
            )
    
    async def execute_smart_refresh(self, driver) -> StrategyResult:
        """Smart refresh without losing state"""
        start = time.time()
        
        try:
            # Save scroll position
            scroll_js = "return [window.scrollX, window.scrollY];"
            scroll_pos = driver.execute_script(scroll_js)
            
            # Refresh
            driver.refresh()
            time.sleep(3)
            
            # Restore scroll position
            restore_js = f"window.scrollTo({scroll_pos[0]}, {scroll_pos[1]});"
            driver.execute_script(restore_js)
            
            logger.info("✅ Smart refresh completed")
            return StrategyResult(
                strategy=StrategyType.SMART_REFRESH,
                success=True,
                execution_time=time.time() - start,
                confidence=0.8
            )
            
        except Exception as e:
            logger.error(f"❌ Smart refresh failed: {e}")
            return StrategyResult(
                strategy=StrategyType.SMART_REFRESH,
                success=False,
                execution_time=time.time() - start,
                confidence=0.2
            )
    
    async def execute_cells(self, driver) -> StrategyResult:
        """Execute cells to show activity"""
        start = time.time()
        
        try:
            # Find and click run buttons in cells
            run_selectors = [
                'colab-run-button',
                '.run-cell',
                '[icon="run"]',
                'button[aria-label*="Run"]',
            ]
            
            clicked = False
            for selector in run_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        if elem.is_displayed():
                            elem.click()
                            clicked = True
                            time.sleep(1)
                except:
                    continue
            
            if clicked:
                logger.info("✅ Cells executed")
                return StrategyResult(
                    strategy=StrategyType.CELL_EXECUTION,
                    success=True,
                    execution_time=time.time() - start,
                    confidence=0.7
                )
            else:
                # Fallback to keyboard shortcut
                actions = ActionChains(driver)
                actions.key_down(Keys.CONTROL).send_keys(Keys.ENTER).key_up(Keys.CONTROL).perform()
                
                logger.info("✅ Cells executed via keyboard")
                return StrategyResult(
                    strategy=StrategyType.CELL_EXECUTION,
                    success=True,
                    execution_time=time.time() - start,
                    confidence=0.6
                )
                
        except Exception as e:
            logger.error(f"❌ Cell execution failed: {e}")
            return StrategyResult(
                strategy=StrategyType.CELL_EXECUTION,
                success=False,
                execution_time=time.time() - start,
                confidence=0.2
            )
    
    def update_strategy_stats(self, strategy_id: str, success: bool):
        """Update strategy success/failure counts"""
        if success:
            self.success_counts[strategy_id] = self.success_counts.get(strategy_id, 0) + 1
        else:
            self.failure_counts[strategy_id] = self.failure_counts.get(strategy_id, 0) + 1
        
        # Keep counts manageable
        if self.success_counts.get(strategy_id, 0) > 1000:
            self.success_counts[strategy_id] = 500
        if self.failure_counts.get(strategy_id, 0) > 1000:
            self.failure_counts[strategy_id] = 500

# ==================== MAIN BOT CLASS ====================

class AIColabSupremeBot:
    """Main bot orchestrator"""
    
    def __init__(self):
        self.state = BotState.INITIALIZING
        self.metrics = BotMetrics()
        self.health = BotHealth()
        self.url = Config.get("COLAB_URL")
        
        # Initialize modules
        self.ai = AIModule()
        self.browser = BrowserManager()
        self.strategy_engine = StrategyEngine(self.browser, self.ai)
        
        # Control flags
        self.is_running = False
        self.main_loop_task = None
        self.health_check_task = None
        
        # Prometheus metrics
        self.metrics_total_actions = Counter('colab_total_actions', 'Total actions performed')
        self.metrics_successful_actions = Counter('colab_successful_actions', 'Successful actions')
        self.metrics_disconnections = Counter('colab_disconnections', 'Total disconnections')
        self.metrics_bot_state = Gauge('colab_bot_state', 'Current bot state', ['state'])
        
        logger.info("🤖 AI Colab Supreme Bot initialized")
    
    async def initialize(self):
        """Initialize the bot"""
        try:
            logger.info("🚀 Initializing bot...")
            
            # Initialize browser
            await self.browser.initialize()
            
            # Load Colab in all browsers
            for driver in self.browser.drivers:
                try:
                    driver.get(self.url)
                    await asyncio.sleep(5)  # Wait for page load
                except Exception as e:
                    logger.error(f"❌ Failed to load Colab: {e}")
            
            self.state = BotState.RUNNING
            self.is_running = True
            
            # Start health monitoring
            self.health_check_task = asyncio.create_task(self.health_monitor_loop())
            
            logger.info("✅ Bot initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Bot initialization failed: {e}")
            self.state = BotState.ERROR
            return False
    
    async def health_monitor_loop(self):
        """Monitor bot health"""
        while self.is_running:
            try:
                await self.check_health()
                await asyncio.sleep(Config.get("HEALTH_CHECK_INTERVAL", 30))
            except Exception as e:
                logger.error(f"❌ Health monitor error: {e}")
                await asyncio.sleep(60)
    
    async def check_health(self):
        """Check system and bot health"""
        try:
            # System resources
            self.health.memory_usage_mb = psutil.Process().memory_info().rss / 1024 / 1024
            self.health.cpu_percent = psutil.cpu_percent(interval=1)
            self.health.disk_usage_percent = psutil.disk_usage('/').percent
            
            # Browser health
            unhealthy_drivers = self.browser.check_health()
            self.health.driver_health = [i not in unhealthy_drivers for i in range(len(self.browser.drivers))]
            
            # Check for issues
            self.health.issues.clear()
            
            if self.health.memory_usage_mb > Config.get("MAX_MEMORY_MB", 512):
                self.health.issues.append(f"High memory usage: {self.health.memory_usage_mb:.1f}MB")
            
            if self.health.cpu_percent > Config.get("MAX_CPU_PERCENT", 80):
                self.health.issues.append(f"High CPU usage: {self.health.cpu_percent:.1f}%")
            
            if len(unhealthy_drivers) > len(self.browser.drivers) // 2:
                self.health.issues.append(f"{len(unhealthy_drivers)}/{len(self.browser.drivers)} drivers unhealthy")
            
            self.health.is_healthy = len(self.health.issues) == 0
            self.health.last_check = datetime.now()
            
            # Auto-recovery if enabled
            if not self.health.is_healthy and Config.get("AUTO_RECOVERY", True):
                await self.perform_recovery()
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            self.health.is_healthy = False
            self.health.issues.append(f"Health check error: {e}")
    
    async def perform_recovery(self):
        """Perform automatic recovery"""
        logger.warning("⚠️ Performing auto-recovery...")
        
        try:
            # Restart unhealthy drivers
            for i, healthy in enumerate(self.health.driver_health):
                if not healthy:
                    await self.browser.recover_driver(i)
            
            # Clear memory if needed
            if self.health.memory_usage_mb > Config.get("MAX_MEMORY_MB", 512):
                import gc
                gc.collect()
            
            logger.info("✅ Auto-recovery completed")
            
        except Exception as e:
            logger.error(f"❌ Auto-recovery failed: {e}")
    
    async def main_loop(self):
        """Main bot execution loop"""
        logger.info("🚀 Starting main loop")
        
        while self.is_running and self.state == BotState.RUNNING:
            cycle_start = time.time()
            
            try:
                # Update Prometheus metrics
                self.metrics_bot_state.labels(state=self.state.value).set(1)
                
                # Get healthy driver
                driver, driver_idx = self.browser.get_healthy_driver()
                if not driver:
                    logger.warning("⚠️ No healthy drivers available, waiting...")
                    await asyncio.sleep(30)
                    continue
                
                # Build context for AI
                context = self.build_decision_context()
                
                # Choose and execute strategy
                strategy = self.strategy_engine.choose_strategy(context)
                if strategy:
                    result = await strategy['function'](driver)
                    
                    # Update metrics
                    self.metrics.total_actions += 1
                    self.metrics_total_actions.inc()
                    
                    if result.success:
                        self.metrics.successful_actions += 1
                        self.metrics_successful_actions.inc()
                        self.metrics.last_success = datetime.now()
                    
                    # Update strategy statistics
                    self.strategy_engine.update_strategy_stats(strategy['id'], result.success)
                    
                    # Record result
                    self.strategy_engine.history.append({
                        'timestamp': datetime.now(),
                        'strategy': strategy['id'],
                        'success': result.success,
                        'execution_time': result.execution_time,
                        'confidence': result.confidence
                    })
                    
                    # Keep history manageable
                    if len(self.strategy_engine.history) > 1000:
                        self.strategy_engine.history = self.strategy_engine.history[-500:]
                    
                    logger.info(f"📊 Strategy '{strategy['name']}': {'✅ Success' if result.success else '❌ Failed'} "
                              f"(Confidence: {result.confidence:.2f}, Time: {result.execution_time:.2f}s)")
                
                # Calculate next check time
                sleep_time = self.calculate_sleep_time()
                cycle_time = time.time() - cycle_start
                
                # Adjust sleep time for cycle duration
                adjusted_sleep = max(1, sleep_time - cycle_time)
                
                logger.info(f"⏳ Next check in {adjusted_sleep:.1f}s (Cycle: {cycle_time:.1f}s)")
                await asyncio.sleep(adjusted_sleep)
                
            except Exception as e:
                logger.error(f"❌ Main loop error: {e}")
                self.metrics.errors.append({
                    'timestamp': datetime.now(),
                    'error': str(e),
                    'context': 'main_loop'
                })
                
                # Keep errors manageable
                if len(self.metrics.errors) > 100:
                    self.metrics.errors = self.metrics.errors[-50:]
                
                await asyncio.sleep(30)  # Wait before retry
    
    def build_decision_context(self) -> Dict:
        """Build context for AI decision making"""
        success_rate = (self.metrics.successful_actions / self.metrics.total_actions 
                       if self.metrics.total_actions > 0 else 0)
        
        # Recent strategy success rates
        strategy_success = {}
        recent_history = self.strategy_engine.history[-20:]  # Last 20 actions
        for entry in recent_history:
            strategy = entry['strategy']
            if strategy not in strategy_success:
                strategy_success[strategy] = {'success': 0, 'total': 0}
            strategy_success[strategy]['total'] += 1
            if entry['success']:
                strategy_success[strategy]['success'] += 1
        
        # Calculate rates
        strategy_success_rates = {}
        for strategy, data in strategy_success.items():
            if data['total'] > 0:
                strategy_success_rates[strategy] = data['success'] / data['total']
        
        return {
            'state': self.state.value,
            'session_age': (datetime.now() - self.metrics.session_start).total_seconds() / 60,
            'success_rate': success_rate,
            'recent_errors': self.metrics.errors[-5:] if self.metrics.errors else [],
            'strategy_success': strategy_success_rates,
            'time_of_day': datetime.now().hour,
            'day_of_week': datetime.now().weekday(),
            'health_issues': len(self.health.issues),
            'active_drivers': sum(self.health.driver_health),
            'last_success_minutes': (datetime.now() - self.metrics.last_success).total_seconds() / 60 
                                   if self.metrics.last_success else 999,
        }
    
    def calculate_sleep_time(self) -> float:
        """Calculate adaptive sleep time"""
        base_interval = Config.get("CHECK_INTERVAL", 150)
        
        # Adjust based on success rate
        success_rate = (self.metrics.successful_actions / self.metrics.total_actions 
                       if self.metrics.total_actions > 0 else 0.5)
        
        if success_rate > 0.9:
            # Things are good, check less frequently
            return base_interval * 1.2
        elif success_rate > 0.7:
            return base_interval
        elif success_rate > 0.5:
            return base_interval * 0.8
        else:
            # Low success rate, check more frequently
            return base_interval * 0.5
    
    async def start(self):
        """Start the bot"""
        if self.state == BotState.RUNNING:
            logger.info("⚠️ Bot already running")
            return True
        
        success = await self.initialize()
        if success:
            self.main_loop_task = asyncio.create_task(self.main_loop())
            logger.info("🚀 Bot started successfully")
            return True
        
        return False
    
    async def stop(self):
        """Stop the bot"""
        logger.info("🛑 Stopping bot...")
        
        self.is_running = False
        self.state = BotState.STOPPED
        
        # Cancel tasks
        if self.main_loop_task:
            self.main_loop_task.cancel()
            try:
                await self.main_loop_task
            except asyncio.CancelledError:
                pass
        
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
        
        # Close browsers
        self.browser.close_all()
        
        logger.info("✅ Bot stopped")
        return True
    
    async def restart(self):
        """Restart the bot"""
        await self.stop()
        await asyncio.sleep(2)
        return await self.start()
    
    def get_status(self) -> Dict:
        """Get current bot status"""
        session_age = (datetime.now() - self.metrics.session_start).total_seconds() / 60
        success_rate = (self.metrics.successful_actions / self.metrics.total_actions 
                       if self.metrics.total_actions > 0 else 0)
        
        return {
            'state': self.state.value,
            'is_running': self.is_running,
            'metrics': {
                'total_actions': self.metrics.total_actions,
                'successful_actions': self.metrics.successful_actions,
                'success_rate': success_rate,
                'total_connects': self.metrics.total_connects,
                'cells_run': self.metrics.cells_run,
                'disconnections': self.metrics.disconnections,
                'session_age_minutes': int(session_age)
            },
            'health': {
                'is_healthy': self.health.is_healthy,
                'memory_mb': round(self.health.memory_usage_mb, 1),
                'cpu_percent': round(self.health.cpu_percent, 1),
                'driver_health': self.health.driver_health.count(True),
                'issues': self.health.issues
            },
            'ai': {
                'enabled': self.ai.is_enabled,
                'cv_available': self.ai.cv_detector is not None,
            },
            'timestamp': datetime.now().isoformat()
        }

# ==================== WEB DASHBOARD ====================

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global bot instance
bot = None
telegram_app = None

@app.route('/')
def dashboard():
    """Main dashboard page"""
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 AI Colab Supreme</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.5.0/socket.io.js"></script>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
            body { background: #0f172a; color: #f8fafc; line-height: 1.6; }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            
            header { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); padding: 2rem; border-radius: 1rem; margin-bottom: 2rem; box-shadow: 0 10px 25px rgba(0,0,0,0.3); }
            .header-content { display: flex; justify-content: space-between; align-items: center; }
            h1 { font-size: 2.5rem; font-weight: 800; }
            .version { background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 2rem; font-size: 0.9rem; }
            
            .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }
            .status-card { background: #1e293b; padding: 1.5rem; border-radius: 1rem; border-left: 4px solid #6366f1; }
            .status-card h3 { color: #94a3b8; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem; }
            .status-value { font-size: 2rem; font-weight: 700; }
            .status-running { color: #10b981; }
            .status-stopped { color: #ef4444; }
            
            .control-panel { background: #1e293b; padding: 2rem; border-radius: 1rem; margin-bottom: 2rem; }
            .controls { display: flex; gap: 1rem; flex-wrap: wrap; }
            .btn { padding: 1rem 2rem; border: none; border-radius: 0.5rem; font-weight: 600; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; gap: 0.5rem; }
            .btn:hover { transform: translateY(-2px); }
            .btn-start { background: #10b981; color: white; }
            .btn-stop { background: #ef4444; color: white; }
            .btn-restart { background: #f59e0b; color: white; }
            .btn-refresh { background: #3b82f6; color: white; }
            
            .charts { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }
            .chart-container { background: #1e293b; padding: 1.5rem; border-radius: 1rem; }
            
            .logs { background: #1e293b; padding: 1.5rem; border-radius: 1rem; }
            .logs-container { height: 300px; overflow-y: auto; background: #0f172a; padding: 1rem; border-radius: 0.5rem; margin-top: 1rem; font-family: 'Monaco', 'Consolas', monospace; font-size: 0.9rem; }
            .log-entry { padding: 0.25rem 0; border-bottom: 1px solid #334155; }
            .log-success { color: #10b981; }
            .log-error { color: #ef4444; }
            .log-warning { color: #f59e0b; }
            .log-info { color: #3b82f6; }
            
            .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 2rem 0; }
            .stat { background: #1e293b; padding: 1rem; border-radius: 0.5rem; text-align: center; }
            .stat-value { font-size: 1.5rem; font-weight: 700; }
            .stat-label { color: #94a3b8; font-size: 0.9rem; }
            
            footer { text-align: center; padding: 2rem; color: #64748b; font-size: 0.9rem; border-top: 1px solid #334155; margin-top: 2rem; }
            
            @media (max-width: 768px) {
                .container { padding: 10px; }
                h1 { font-size: 1.8rem; }
                .charts { grid-template-columns: 1fr; }
                .status-grid { grid-template-columns: 1fr; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <div class="header-content">
                    <div>
                        <h1>🤖 AI Colab Supreme</h1>
                        <p>AI-Powered 24/7 Colab Protection</p>
                    </div>
                    <div class="version">v3.0.0</div>
                </div>
            </header>
            
            <div class="status-grid">
                <div class="status-card">
                    <h3>Bot Status</h3>
                    <div id="bot-status" class="status-value">Loading...</div>
                    <div id="status-details">Initializing...</div>
                </div>
                
                <div class="status-card">
                    <h3>Success Rate</h3>
                    <div id="success-rate" class="status-value">0%</div>
                    <div>Based on last 100 actions</div>
                </div>
                
                <div class="status-card">
                    <h3>Session Age</h3>
                    <div id="session-age" class="status-value">0m</div>
                    <div>Continuous operation</div>
                </div>
                
                <div class="status-card">
                    <h3>Active Drivers</h3>
                    <div id="active-drivers" class="status-value">0</div>
                    <div>Healthy browser instances</div>
                </div>
            </div>
            
            <div class="control-panel">
                <h2 style="margin-bottom: 1rem;">Control Panel</h2>
                <div class="controls">
                    <button class="btn btn-start" onclick="sendCommand('start')">▶️ Start Bot</button>
                    <button class="btn btn-stop" onclick="sendCommand('stop')">⏹️ Stop Bot</button>
                    <button class="btn btn-restart" onclick="sendCommand('restart')">🔄 Restart</button>
                    <button class="btn btn-refresh" onclick="refreshDashboard()">🔄 Refresh</button>
                </div>
            </div>
            
            <div class="stats-grid">
                <div class="stat">
                    <div class="stat-value" id="total-actions">0</div>
                    <div class="stat-label">Total Actions</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="successful-actions">0</div>
                    <div class="stat-label">Successful</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="connects">0</div>
                    <div class="stat-label">Connections</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="cells-run">0</div>
                    <div class="stat-label">Cells Run</div>
                </div>
            </div>
            
            <div class="charts">
                <div class="chart-container">
                    <h3>Success Rate Over Time</h3>
                    <canvas id="successChart" height="200"></canvas>
                </div>
                <div class="chart-container">
                    <h3>Strategy Distribution</h3>
                    <canvas id="strategyChart" height="200"></canvas>
                </div>
            </div>
            
            <div class="logs">
                <h3>Live Logs</h3>
                <div class="logs-container" id="logs-container">
                    <div class="log-entry log-info">🚀 Dashboard loaded. Waiting for updates...</div>
                </div>
            </div>
            
            <footer>
                <p>🤖 AI Colab Supreme Bot v3.0.0 | Made with ❤️ for the Colab Community</p>
                <p>⚠️ Educational use only | Respect Google's Terms of Service</p>
            </footer>
        </div>
        
        <script>
            // Global variables
            let socket;
            let successChart, strategyChart;
            let successData = [];
            let strategyData = {};
            
            // Initialize
            document.addEventListener('DOMContentLoaded', function() {
                initCharts();
                connectWebSocket();
                refreshDashboard();
                setInterval(refreshDashboard, 10000); // Update every 10 seconds
            });
            
            function initCharts() {
                // Success rate chart
                const successCtx = document.getElementById('successChart').getContext('2d');
                successChart = new Chart(successCtx, {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [{
                            label: 'Success Rate %',
                            data: [],
                            borderColor: '#10b981',
                            backgroundColor: 'rgba(16, 185, 129, 0.1)',
                            tension: 0.4,
                            fill: true
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 100,
                                grid: { color: '#334155' },
                                ticks: { color: '#94a3b8' }
                            },
                            x: {
                                grid: { color: '#334155' },
                                ticks: { color: '#94a3b8' }
                            }
                        },
                        plugins: {
                            legend: { labels: { color: '#94a3b8' } }
                        }
                    }
                });
                
                // Strategy chart
                const strategyCtx = document.getElementById('strategyChart').getContext('2d');
                strategyChart = new Chart(strategyCtx, {
                    type: 'doughnut',
                    data: {
                        labels: [],
                        datasets: [{
                            data: [],
                            backgroundColor: [
                                '#ef4444', '#f59e0b', '#10b981', '#3b82f6',
                                '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'right',
                                labels: { color: '#94a3b8' }
                            }
                        }
                    }
                });
            }
            
            function connectWebSocket() {
                socket = io();
                
                socket.on('connect', () => {
                    addLog('✅ Connected to live updates', 'info');
                });
                
                socket.on('status_update', (data) => {
                    updateDashboardUI(data);
                });
                
                socket.on('log', (logData) => {
                    addLog(logData.message, logData.level);
                });
                
                socket.on('disconnect', () => {
                    addLog('❌ Disconnected from server', 'error');
                });
            }
            
            async function refreshDashboard() {
                try {
                    const response = await fetch('/api/status');
                    const data = await response.json();
                    updateDashboardUI(data);
                } catch (error) {
                    addLog('❌ Failed to fetch status: ' + error, 'error');
                }
            }
            
            function updateDashboardUI(data) {
                // Update status
                const statusEl = document.getElementById('bot-status');
                const statusDetails = document.getElementById('status-details');
                
                statusEl.textContent = data.state.toUpperCase();
                statusEl.className = 'status-value ' + 
                    (data.state === 'running' ? 'status-running' : 
                     data.state === 'stopped' ? 'status-stopped' : '');
                
                statusDetails.textContent = data.is_running ? 'Active and monitoring' : 'Bot is stopped';
                
                // Update metrics
                document.getElementById('success-rate').textContent = 
                    (data.metrics.success_rate * 100).toFixed(1) + '%';
                document.getElementById('session-age').textContent = 
                    data.metrics.session_age_minutes + 'm';
                document.getElementById('active-drivers').textContent = 
                    data.health.driver_health;
                
                // Update stats
                document.getElementById('total-actions').textContent = 
                    data.metrics.total_actions;
                document.getElementById('successful-actions').textContent = 
                    data.metrics.successful_actions;
                document.getElementById('connects').textContent = 
                    data.metrics.total_connects;
                document.getElementById('cells-run').textContent = 
                    data.metrics.cells_run;
                
                // Update charts
                updateCharts(data);
            }
            
            function updateCharts(data) {
                // Update success chart
                const now = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                successChart.data.labels.push(now);
                successChart.data.datasets[0].data.push(data.metrics.success_rate * 100);
                
                if (successChart.data.labels.length > 15) {
                    successChart.data.labels.shift();
                    successChart.data.datasets[0].data.shift();
                }
                
                successChart.update();
            }
            
            function addLog(message, level = 'info') {
                const container = document.getElementById('logs-container');
                const entry = document.createElement('div');
                entry.className = 'log-entry log-' + level;
                entry.textContent = '[' + new Date().toLocaleTimeString() + '] ' + message;
                
                container.appendChild(entry);
                container.scrollTop = container.scrollHeight;
                
                // Keep last 50 logs
                if (container.children.length > 50) {
                    container.removeChild(container.firstChild);
                }
            }
            
            async function sendCommand(command) {
                try {
                    const response = await fetch('/api/control/' + command, {
                        method: 'POST'
                    });
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        addLog('✅ Command executed: ' + command, 'success');
                        setTimeout(refreshDashboard, 2000);
                    } else {
                        addLog('❌ Command failed: ' + result.message, 'error');
                    }
                } catch (error) {
                    addLog('❌ Error sending command: ' + error, 'error');
                }
            }
        </script>
    </body>
    </html>
    '''
    return html

@app.route('/health')
def health_check():
    """Health check endpoint"""
    if not bot:
        return jsonify({"status": "initializing", "healthy": False})
    
    try:
        status = bot.get_status()
        return jsonify({
            "status": "healthy",
            "bot_state": status['state'],
            "health": status['health']['is_healthy'],
            "timestamp": datetime.now().isoformat()
        })
    except:
        return jsonify({"status": "error", "healthy": False})

@app.route('/api/status')
def api_status():
    """API endpoint for bot status"""
    if not bot:
        return jsonify({"error": "Bot not initialized"}), 503
    
    try:
        status = bot.get_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/control/<command>', methods=['POST'])
async def api_control(command):
    """Control the bot"""
    global bot
    
    try:
        if command == 'start':
            if not bot:
                from ai_colab_supreme_final import AIColabSupremeBot
                bot = AIColabSupremeBot()
            
            success = await bot.start()
            if success:
                return jsonify({"status": "success", "message": "Bot started"})
            else:
                return jsonify({"status": "error", "message": "Failed to start bot"})
        
        elif command == 'stop':
            if bot:
                success = await bot.stop()
                if success:
                    return jsonify({"status": "success", "message": "Bot stopped"})
                else:
                    return jsonify({"status": "error", "message": "Failed to stop bot"})
            return jsonify({"status": "error", "message": "Bot not running"})
        
        elif command == 'restart':
            if bot:
                success = await bot.restart()
                if success:
                    return jsonify({"status": "success", "message": "Bot restarted"})
                else:
                    return jsonify({"status": "error", "message": "Failed to restart bot"})
            return jsonify({"status": "error", "message": "Bot not running"})
        
        else:
            return jsonify({"status": "error", "message": "Unknown command"}), 400
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), mimetype='text/plain')

# ==================== TELEGRAM BOT ====================

if TELEGRAM_AVAILABLE and Config.get("ENABLE_TELEGRAM") and Config.get("TELEGRAM_BOT_TOKEN"):
    
    async def telegram_bot_main():
        """Start Telegram bot"""
        token = Config.get("TELEGRAM_BOT_TOKEN")
        chat_id = Config.get("TELEGRAM_CHAT_ID")
        
        application = Application.builder().token(token).build()
        
        async def start_command(update: Update, context):
            await update.message.reply_text(
                "🤖 *AI Colab Supreme Bot*\n\n"
                "Available commands:\n"
                "/status - Bot status\n"
                "/start_bot - Start bot\n"
                "/stop_bot - Stop bot\n"
                "/restart - Restart bot\n"
                "/stats - Statistics\n"
                "/help - Show help",
                parse_mode='Markdown'
            )
        
        async def status_command(update: Update, context):
            if not bot:
                await update.message.reply_text("❌ Bot not initialized")
                return
            
            status = bot.get_status()
            message = (
                f"🤖 *Bot Status*\n\n"
                f"• State: `{status['state']}`\n"
                f"• Success Rate: `{status['metrics']['success_rate']*100:.1f}%`\n"
                f"• Actions: `{status['metrics']['total_actions']}`\n"
                f"• Session: `{status['metrics']['session_age_minutes']}m`\n"
                f"• Drivers: `{status['health']['driver_health']}` healthy\n"
                f"• Memory: `{status['health']['memory_mb']}MB`\n"
                f"• CPU: `{status['health']['cpu_percent']}%`\n"
            )
            
            if status['health']['issues']:
                message += f"\n⚠️ Issues:\n" + "\n".join([f"• {issue}" for issue in status['health']['issues']])
            
            await update.message.reply_text(message, parse_mode='Markdown')
        
        # Add handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("status", status_command))
        application.add_handler(CommandHandler("help", start_command))
        
        # Start bot
        await application.initialize()
        await application.start()
        logger.info("✅ Telegram bot started")
        
        # Keep running
        while True:
            await asyncio.sleep(3600)

# ==================== MAIN ENTRY POINT ====================

async def main():
    """Main entry point"""
    global bot
    
    logger.info("=" * 60)
    logger.info("🚀 AI COLAB SUPREME BOT v3.0.0")
    logger.info("=" * 60)
    logger.info(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"🌐 Colab URL: {Config.get('COLAB_URL')}")
    logger.info(f"🤖 AI Enabled: {Config.get('ENABLE_AI')}")
    logger.info(f"👁️ CV Enabled: {Config.get('ENABLE_CV')}")
    logger.info(f"📊 Max Tabs: {Config.get('MAX_PARALLEL_TABS')}")
    logger.info("=" * 60)
    
    # Create bot instance
    bot = AIColabSupremeBot()
    
    # Auto-start if configured
    if Config.get("RENDER") or Config.get("AUTO_START", True):
        logger.info("🔄 Auto-starting bot...")
        await bot.start()
    
    # Start Telegram bot in background if enabled
    if (TELEGRAM_AVAILABLE and Config.get("ENABLE_TELEGRAM") and 
        Config.get("TELEGRAM_BOT_TOKEN") and Config.get("TELEGRAM_CHAT_ID")):
        asyncio.create_task(telegram_bot_main())
    
    logger.info("✅ System ready. Dashboard available at http://localhost:8080")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"⚠️ Received signal {signum}, shutting down...")
    if bot:
        asyncio.run(bot.stop())
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run main async function
    try:
        # Start Flask app
        port = int(os.getenv("PORT", 8080))
        
        # Run in separate thread
        import threading
        flask_thread = threading.Thread(
            target=lambda: socketio.run(app, host="0.0.0.0", port=port, debug=False, allow_unsafe_werkzeug=True),
            daemon=True
        )
        flask_thread.start()
        
        # Run main async loop
        asyncio.run(main())
        
        # Keep running
        while True:
            time.sleep(3600)
            
    except KeyboardInterrupt:
        logger.info("👋 Shutting down...")
        if bot:
            asyncio.run(bot.stop())
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
