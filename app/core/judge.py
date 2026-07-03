from app.core.llm_client import llm_client
from app.config import settings
from app.schemas import EvalResult
import logging

logger = logging.getLogger(__name__)

async def run_judge(evaluation_criteria: str, llm_output_to_grade: str) -> EvalResult:
    """
    Uses DeepSeek to grade an LLM output based on strict criteria.
    Enforces structured JSON output validated by Pydantic.
    """
    
    # System Prompt: Define the persona and strict formatting rules
    system_prompt = """You are an expert AI Evaluator (LLM-as-a-Judge) for a production AI platform.
    Your task is to evaluate the provided LLM output based strictly on the given criteria.
    
    RULES:
    1. You MUST output ONLY valid JSON.
    2. Do NOT include markdown formatting (like ```json).
    3. Do NOT include any conversational text outside the JSON object.
    4. The JSON must contain exactly two keys: 'score' (integer 1-5) and 'reasoning' (string).
    """
    
    user_prompt = f"""
    CRITERIA: {evaluation_criteria}
    
    LLM OUTPUT TO GRADE: 
    {llm_output_to_grade}
    """
    
    try:
        response = await llm_client.chat.completions.create(
            model=settings.DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1 # Low temperature for strict, deterministic grading
        )
        
        raw_json_str = response.choices[0].message.content
        logger.debug(f"Raw LLM Judge Output: {raw_json_str}")
        
        # Pydantic parses and validates the JSON against our EvalResult schema
        return EvalResult.model_validate_json(raw_json_str)
        
    except Exception as e:
        logger.error(f"Judge execution failed: {e}")
        # In production, you might want to return a default "Error" object 
        # rather than crashing the entire batch evaluation.
        raise RuntimeError(f"Failed to get valid evaluation from LLM: {str(e)}")