import time
import uuid
import logging
from sqlmodel import Session, select
from app.database import engine
from app.models import Experiment, EvalRun, Prompt, DatasetItem
from app.core.llm_client import llm_client
from app.core.judge import run_judge
from app.config import settings

logger = logging.getLogger(__name__)

async def execute_experiment(experiment_id: uuid.UUID):
    """
    Background task that executes the evaluation pipeline.
    It render prompts, calls the LLM to generate text, and calls the Judge to grade it.
    """
    logger.info(f"Starting background execution for Experiment: {experiment_id}")

    with Session(engine) as session:
        experiment = session.get(Experiment, experiment_id)
        if not experiment:
            logger.error(f"Experiment {experiment_id} not found.")
            return
        
        experiment.status = "RUNNING"
        session.add(experiment)
        session.commit()

        # fetch dependencies
        prompt = session.get(Prompt, experiment.prompt_id)
        items = session.exec(select(DatasetItem).where(DatasetItem.dataset_id == experiment.dataset_id)).all()

        if not prompt or not items:
            logger.error("Prompt or Dataset Items missing. Failing experiment.")
            experiment.status = "FAILED"
            session.add(experiment)
            session.commit()
            return
        
        scores = []

        for item in items:
            try:
                # 1. Render prompt
                input_dict = item.input_data

                if isinstance(input_dict, str):
                    input_dict = json.loads(input_dict)

                rendered_prompt = prompt.template.format(**input_dict)

                start_time = time.time()

                # 2. Call deepseek to gen output
                response = await llm_client.chat.completions.create(
                    model = settings.DEEPSEEK_MODEL,
                    messages = [{"role": "user", "content": rendered_prompt}]
                )
                generated_text = response.choices[0].message.content
                latency_ms = int((time.time() - start_time) * 1000)

                # 3. call the llm judge
                judge_result = await run_judge(experiment.criteria, input_dict, generated_text)

                # 4. save individual run to db
                eval_run = EvalRun(
                    experiment_id = experiment_id,
                    dataset_item_id = item.id,
                    generated_output = generated_text,
                    judge_score = judge_result.score,
                    judge_reasoning = judge_result.reasoning,
                    latency_ms = latency_ms
                )
                session.add(eval_run)
                scores.append(judge_result.score)

                # commit after every item
                # if deepseek goes down halfway through, we dont lose the first rows
                session.commit()

            except KeyError as ke:
                logger.warning(f"Prompt variable mismatch on item {item.id}: {ke}")
            except Exception as e:
                logger.error(f"Error evaluating item {item.id}: {e}")

        # 5. Finalize Metrics
        experiment.total_items = len(items)
        experiment.avg_score = sum(scores) / len(scores) if scores else 0.0
        experiment.status = "COMPLETED"

        session.add(experiment)
        session.commit()
        logger.info(f"Experiment {experiment_id} COMPLETED. Avg Score: {experiment.avg_score:.2f}")
                