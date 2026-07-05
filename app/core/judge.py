import re
import json
from app.core.llm_client import llm_client
from app.config import settings
from app.schemas import EvalResult
import logging

logger = logging.getLogger(__name__)

def clean_and_parse_json(raw_text: str) -> dict:
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw_text)
    
    if match:
        raw_text = match.group(1)
    start = raw_text.find('{')
    end = raw_text.find('}')

    if start != -1 and end != -1 and end > start:
        raw_text = raw_text[start:end+1]
    return json.loads(raw_text)


async def run_judge(evaluation_criteria: str, original_input_data: str, llm_output_to_grade: str) -> EvalResult:
    """
    Uses DeepSeek to grade an LLM output based on strict criteria.
    Enforces structured JSON output validated by Pydantic.
    """

    input_str = json.dumps(original_input_data, indent=2)
    
    # System Prompt: Define the persona and strict formatting rules
    system_prompt = """You are an expert AI Evaluator (LLM-as-a-Judge) for a production AI platform.
    Your task is to evaluate the BUSINESS ACCURACY of the LLM's output based strictly on the provided CRITERIA and the ORIGINAL INPUT DATA.
    
    CRITICAL WARNINGS:
    1. DO NOT evaluate if the LLM followed formatting instructions. Evaluate if the output is FACTUALLY CORRECT based on the input data.
    2. If the LLM was tricked into ignoring the data, or if it outputs a sentiment without any reasoning or context, it is a FAILURE. Score it 1.
    3. You MUST output ONLY valid JSON. No markdown, no conversational text.
    4. JSON keys: 'score' (integer 1-5) and 'reasoning' (string).
    """
    
    user_prompt = f"""
    CRITERIA: {evaluation_criteria}

    ORIGINAL INPUT DATA (The ground truth context):
    {input_str}
    
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
        clean_dict = clean_and_parse_json(raw_json_str)
        logger.debug(f"Raw LLM Judge Output: {raw_json_str}")
        
        # Pydantic parses and validates the JSON against our EvalResult schema
        return EvalResult.model_validate(clean_dict)
        
    except Exception as e:
        logger.error(f"Judge execution failed: {e}")
        # In production, you might want to return a default "Error" object 
        # rather than crashing the entire batch evaluation.
        raise RuntimeError(f"Failed to get valid evaluation from LLM: {str(e)}")