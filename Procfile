# For multiple process types (Render.com style)
web: gunicorn --workers=2 --threads=4 --bind=0.0.0.0:$PORT ai_colab_supreme_final:app
worker: python ai_colab_supreme_final.py
telegram: python -c "
import asyncio
from ai_colab_supreme_final import Config
if Config.get('ENABLE_TELEGRAM') and Config.get('TELEGRAM_BOT_TOKEN'):
    import telegram_bot
    asyncio.run(telegram_bot.start())
"

# Alternative: Single process (simpler)
web: python ai_colab_supreme_final.py

# Alternative: Gunicorn with WebSocket support
web: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT ai_colab_supreme_final:app

# Alternative: Uvicorn for async (fastest)
web: uvicorn ai_colab_supreme_final:app --host 0.0.0.0 --port $PORT --workers 1
