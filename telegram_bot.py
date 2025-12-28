#!/usr/bin/env python3
"""
🤖 Telegram Bot for AI Colab Supreme
Real-time notifications and control
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import Optional

from telegram import Update, Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global bot instance (from main app)
colab_bot = None

class ColabTelegramBot:
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.application = None
        self.bot = None
        
    async def start(self):
        """Start the Telegram bot"""
        try:
            self.application = Application.builder().token(self.token).build()
            self.bot = self.application.bot
            
            # Add command handlers
            self.add_handlers()
            
            # Start polling
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            logger.info("✅ Telegram bot started successfully")
            
            # Send startup message
            await self.send_message("🤖 *AI Colab Supreme Bot Started*\n\nBot is now active and monitoring your Colab notebook.", parse_mode='Markdown')
            
            return True
        except Exception as e:
            logger.error(f"❌ Failed to start Telegram bot: {e}")
            return False
    
    def add_handlers(self):
        """Add all command handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.cmd_start))
        self.application.add_handler(CommandHandler("help", self.cmd_help))
        self.application.add_handler(CommandHandler("status", self.cmd_status))
        self.application.add_handler(CommandHandler("stats", self.cmd_stats))
        self.application.add_handler(CommandHandler("strategies", self.cmd_strategies))
        self.application.add_handler(CommandHandler("start_bot", self.cmd_start_bot))
        self.application.add_handler(CommandHandler("stop_bot", self.cmd_stop_bot))
        self.application.add_handler(CommandHandler("restart", self.cmd_restart))
        self.application.add_handler(CommandHandler("screenshot", self.cmd_screenshot))
        self.application.add_handler(CommandHandler("logs", self.cmd_logs))
        self.application.add_handler(CommandHandler("alerts", self.cmd_alerts))
        
        # Callback query handler for buttons
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Error handler
        self.application.add_error_handler(self.error_handler)
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        keyboard = [
            [
                InlineKeyboardButton("📊 Status", callback_data='status'),
                InlineKeyboardButton("⚡ Start Bot", callback_data='start_bot')
            ],
            [
                InlineKeyboardButton("📈 Statistics", callback_data='stats'),
                InlineKeyboardButton("🛠️ Strategies", callback_data='strategies')
            ],
            [
                InlineKeyboardButton("🔄 Restart", callback_data='restart'),
                InlineKeyboardButton("🛑 Stop", callback_data='stop_bot')
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = """
🤖 *AI Colab Supreme Bot*

*Features:*
• 🤖 AI-Powered decision making
• 👁️ Computer Vision detection
• 📊 Predictive analytics
• 🛡️ 12+ protection strategies
• 📱 Real-time monitoring

*Commands:*
/status - Current bot status
/stats - Detailed statistics
/strategies - Active strategies
/start_bot - Start the bot
/stop_bot - Stop the bot
/restart - Restart bot
/screenshot - Get screenshot
/logs - Recent logs
/alerts - Configure alerts

Click buttons below or use commands!
        """
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
*Available Commands:*

*Control:*
/start_bot - Start the Colab bot
/stop_bot - Stop the bot
/restart - Restart bot
/status - Current status

*Monitoring:*
/stats - Detailed statistics
/strategies - Active strategies
/screenshot - Get Colab screenshot
/logs - View recent logs

*Configuration:*
/alerts - Configure notifications
/settings - Bot settings

*Quick Actions:*
/force_reconnect - Force reconnection
/run_cells - Run all cells
/refresh - Refresh Colab

Use buttons or commands to control the bot!
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        if not colab_bot:
            await update.message.reply_text("❌ Bot not initialized")
            return
        
        # Get status from colab_bot
        status = colab_bot.state.value if hasattr(colab_bot, 'state') else 'unknown'
        drivers = len(colab_bot.drivers) if hasattr(colab_bot, 'drivers') else 0
        
        status_text = f"""
*🤖 Bot Status*

*State:* {status.upper()}
*Active Drivers:* {drivers}
*AI Engine:* {'✅ Active' if colab_bot.ai_engine else '❌ Inactive'}
*CV Detection:* {'✅ Active' if colab_bot.cv_detector.model else '❌ Inactive'}

*Last Action:* {colab_bot.metrics.total_actions if hasattr(colab_bot, 'metrics') else 0}
*Success Rate:* {(colab_bot.metrics.successful_actions / colab_bot.metrics.total_actions * 100) if hasattr(colab_bot, 'metrics') and colab_bot.metrics.total_actions > 0 else 0:.1f}%

🟢 *Bot is {'RUNNING' if status == 'running' else 'NOT RUNNING'}*
        """
        
        await update.message.reply_text(status_text, parse_mode='Markdown')
    
    async def cmd_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        if not colab_bot:
            await update.message.reply_text("❌ Bot not initialized")
            return
        
        metrics = colab_bot.metrics if hasattr(colab_bot, 'metrics') else None
        
        if not metrics:
            stats_text = "*📊 Statistics*\n\nNo metrics available yet."
        else:
            success_rate = (metrics.successful_actions / metrics.total_actions * 100) if metrics.total_actions > 0 else 0
            
            stats_text = f"""
*📊 Detailed Statistics*

*Performance Metrics:*
• Total Actions: `{metrics.total_actions}`
• Successful: `{metrics.successful_actions}`
• Success Rate: `{success_rate:.1f}%`
• Connections: `{metrics.total_connects}`
• Cells Run: `{metrics.cells_run}`
• Disconnections: `{metrics.disconnections}`

*Strategy Success Rates:*
"""
            # Add strategy success rates
            for strategy, rate in metrics.strategy_success_rate.items():
                stats_text += f"• {strategy}: `{rate:.1%}`\n"
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')
    
    async def cmd_strategies(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /strategies command"""
        if not colab_bot:
            await update.message.reply_text("❌ Bot not initialized")
            return
        
        strategies_text = "*🛠️ Active Strategies*\n\n"
        
        for i, strategy in enumerate(colab_bot.strategies, 1):
            if strategy['enabled']:
                strategies_text += f"{i}. *{strategy['name']}*\n"
                strategies_text += f"   Type: `{strategy['type'].value}`\n"
                strategies_text += f"   Weight: `{strategy['weight']:.2f}`\n"
                strategies_text += f"   Status: {'✅ Enabled'}\n\n"
        
        # Add AI decision info
        if colab_bot.ai_engine:
            strategies_text += "\n*🤖 AI Decision Engine*\n"
            strategies_text += "✅ Active - AI chooses optimal strategies"
        else:
            strategies_text += "\n*🤖 AI Decision Engine*\n"
            strategies_text += "❌ Inactive - Using fixed strategy weights"
        
        await update.message.reply_text(strategies_text, parse_mode='Markdown')
    
    async def cmd_start_bot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start_bot command"""
        global colab_bot
        
        if colab_bot and colab_bot.state.value == 'running':
            await update.message.reply_text("✅ Bot is already running!")
            return
        
        from ai_colab_supreme import AIColabSupremeBot
        colab_bot = AIColabSupremeBot()
        
        try:
            success = await colab_bot.start()
            if success:
                await update.message.reply_text("🚀 *Bot started successfully!*\n\nAI Colab Supreme is now active and protecting your notebook.", parse_mode='Markdown')
                
                # Send notification to admin chat
                await self.send_message(
                    f"🚀 Bot started by {update.effective_user.username or 'Unknown'}",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text("❌ Failed to start bot. Check logs for details.")
        except Exception as e:
            await update.message.reply_text(f"❌ Error starting bot: {str(e)}")
    
    async def cmd_stop_bot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stop_bot command"""
        global colab_bot
        
        if not colab_bot:
            await update.message.reply_text("❌ Bot not running")
            return
        
        try:
            success = await colab_bot.stop()
            if success:
                await update.message.reply_text("🛑 *Bot stopped successfully!*", parse_mode='Markdown')
                
                # Send notification
                await self.send_message(
                    f"🛑 Bot stopped by {update.effective_user.username or 'Unknown'}",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text("❌ Failed to stop bot")
        except Exception as e:
            await update.message.reply_text(f"❌ Error stopping bot: {str(e)}")
    
    async def cmd_restart(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /restart command"""
        global colab_bot
        
        if colab_bot:
            await colab_bot.stop()
        
        from ai_colab_supreme import AIColabSupremeBot
        colab_bot = AIColabSupremeBot()
        
        try:
            success = await colab_bot.start()
            if success:
                await update.message.reply_text("🔄 *Bot restarted successfully!*", parse_mode='Markdown')
                
                # Send notification
                await self.send_message(
                    f"🔄 Bot restarted by {update.effective_user.username or 'Unknown'}",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text("❌ Failed to restart bot")
        except Exception as e:
            await update.message.reply_text(f"❌ Error restarting bot: {str(e)}")
    
    async def cmd_screenshot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /screenshot command"""
        if not colab_bot or not colab_bot.drivers:
            await update.message.reply_text("❌ Bot not running or no drivers available")
            return
        
        try:
            # Take screenshot from first driver
            screenshot_path = f"screenshot_{int(datetime.now().timestamp())}.png"
            colab_bot.drivers[0].save_screenshot(screenshot_path)
            
            # Send photo
            with open(screenshot_path, 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption="📸 *Colab Screenshot*\nCurrent view of your notebook",
                    parse_mode='Markdown'
                )
            
            # Cleanup
            os.remove(screenshot_path)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to get screenshot: {str(e)}")
    
    async def cmd_logs(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /logs command"""
        try:
            # Read last 20 lines from log file
            log_file = "ai_colab_bot.log"
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    lines = f.readlines()[-20:]  # Last 20 lines
                
                logs_text = "*📋 Recent Logs*\n\n"
                logs_text += "```\n"
                logs_text += "".join(lines[-10:])  # Last 10 lines for Telegram
                logs_text += "\n```"
                
                await update.message.reply_text(logs_text, parse_mode='Markdown')
            else:
                await update.message.reply_text("📋 No logs found yet")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Error reading logs: {str(e)}")
    
    async def cmd_alerts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /alerts command"""
        keyboard = [
            [
                InlineKeyboardButton("✅ Enable All", callback_data='alerts_enable_all'),
                InlineKeyboardButton("❌ Disable All", callback_data='alerts_disable_all')
            ],
            [
                InlineKeyboardButton("🔔 Disconnection Alerts", callback_data='alert_disc'),
                InlineKeyboardButton("✅ Success Alerts", callback_data='alert_success')
            ],
            [
                InlineKeyboardButton("⚠️ Error Alerts", callback_data='alert_error'),
                InlineKeyboardButton("📊 Daily Report", callback_data='alert_daily')
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data='back_to_main')
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        alerts_text = """
*🔔 Alert Configuration*

Configure what notifications you want to receive:

• *Disconnection Alerts* - When Colab disconnects
• *Success Alerts* - When bot successfully reconnects
• *Error Alerts* - When errors occur
• *Daily Report* - Daily summary at 8 AM

*Current Status:*
✅ All alerts enabled
        """
        
        await update.message.reply_text(
            alerts_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from buttons"""
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        
        if callback_data == 'status':
            await self.cmd_status(query.message, context)
        elif callback_data == 'stats':
            await self.cmd_stats(query.message, context)
        elif callback_data == 'strategies':
            await self.cmd_strategies(query.message, context)
        elif callback_data == 'start_bot':
            await self.cmd_start_bot(query.message, context)
        elif callback_data == 'stop_bot':
            await self.cmd_stop_bot(query.message, context)
        elif callback_data == 'restart':
            await self.cmd_restart(query.message, context)
        elif callback_data == 'back_to_main':
            await self.cmd_start(query.message, context)
        # Add more callback handlers as needed
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Telegram bot error: {context.error}")
        
        # Notify admin of critical errors
        if context.error:
            error_msg = f"❌ Telegram Bot Error:\n```\n{str(context.error)[:200]}\n```"
            await self.send_message(error_msg, parse_mode='Markdown')
    
    async def send_message(self, text: str, parse_mode: Optional[str] = None):
        """Send message to configured chat"""
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode=parse_mode
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    async def send_alert(self, alert_type: str, message: str):
        """Send alert notification"""
        icons = {
            'disconnection': '🔴',
            'reconnection': '🟢',
            'error': '⚠️',
            'warning': '🚨',
            'info': 'ℹ️',
            'success': '✅'
        }
        
        icon = icons.get(alert_type, '📢')
        
        alert_text = f"{icon} *{alert_type.upper()} ALERT*\n\n{message}"
        
        await self.send_message(alert_text, parse_mode='Markdown')
    
    async def send_daily_report(self):
        """Send daily report"""
        if not colab_bot:
            return
        
        metrics = colab_bot.metrics
        
        report = f"""
📊 *DAILY REPORT - {datetime.now().strftime('%Y-%m-%d')}*

*24-Hour Performance:*
• Total Actions: `{metrics.total_actions}`
• Successful: `{metrics.successful_actions}`
• Success Rate: `{(metrics.successful_actions / metrics.total_actions * 100) if metrics.total_actions > 0 else 0:.1f}%`
• Disconnections: `{metrics.disconnections}`
• Avg Recovery Time: `{metrics.recovery_time_avg:.1f}s`

*Top Strategies:*
"""
        # Add top 3 strategies
        sorted_strategies = sorted(
            metrics.strategy_success_rate.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        for i, (strategy, rate) in enumerate(sorted_strategies, 1):
            report += f"{i}. {strategy}: `{rate:.1%}`\n"
        
        report += f"\n*Bot Status:* {'🟢 RUNNING' if colab_bot.state.value == 'running' else '🔴 STOPPED'}"
        
        await self.send_message(report, parse_mode='Markdown')

async def start_telegram_bot():
    """Start Telegram bot standalone"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        logger.warning("⚠️ Telegram credentials not set")
        return
    
    bot = ColabTelegramBot(token, chat_id)
    await bot.start()
    
    # Keep running
    while True:
        await asyncio.sleep(3600)  # Sleep for 1 hour

if __name__ == "__main__":
    asyncio.run(start_telegram_bot())
