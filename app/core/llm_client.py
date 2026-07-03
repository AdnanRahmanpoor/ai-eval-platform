from openai import AsyncOpenAI
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Instantiate once at module level, this will act as a singleton and maintain HTTP pool
llm_client = AsyncOpenAI(
    api_key=settings.DEEPSEEK_API_KEY, 
    base_url=settings.DEEPSEEK_BASE_URL
    )

async def check_llm_health() -> bool:
    """
        Pings the LLM API to ensure service is up & credentials are correct.
    """
    try:
        logger.info("Pinging DeepSeek API for health check...")
        response = await llm_client.chat.completions.create(
            model=settings.DEEPSEEK_MODEL,
            messages=[{"role": "user", "content": "Ping"}],
            max_tokens=5
        )
        logger.info("Deepseek API health check successful.")
        return True
    except Exception as e:
        logger.error(f"DeepSeek API health check FAILED: {e}")
        return False