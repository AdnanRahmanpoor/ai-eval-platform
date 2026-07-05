import httpx
import logging
from app.config import settings

logger = logging.getLogger(__name__)

async def send_telegram_alert(message: str):
    """
    Sends an asynchronous alert to a specified Telegram chat.
    Fails gracefully if credentials are missing.
    """
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        logger.warning("Telegram credentials not configured. Skipping alert.")
        return
    
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": settings.TELEGRAM_CHAT_ID,
        "text": message,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json = payload, timeout = 5.0)
            response.raise_for_status()
            logger.info("Telegram alert sent successfully.")
    except Exception as  e:
        logger.error(f"Failed to send Telegram alert: {e}")