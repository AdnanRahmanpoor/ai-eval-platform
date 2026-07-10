from celery import Celery
from app.config import settings
from app.core.tracing import setup_observalibility

setup_observalibility()

# init celery with redis
celery_app = Celery(
	"worker",
	broker = settings.REDIS_URL,
	backend = settings.REDIS_URL,
	include = ["app.services.eval_engine"] # where to find tasks
)

# celery config
celery_app.conf.update(
	task_track_started = True,
	task_time_limit = 3600, # 1 hr max per task
	worker_prefetch_multiplier = 1,
)