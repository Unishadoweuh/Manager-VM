from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "unimanager",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.billing",
        "app.tasks.monitoring"
    ]
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    "process-vm-billing": {
        "task": "app.tasks.billing.process_vm_billing",
        "schedule": crontab(minute=f"*/{settings.BILLING_CYCLE_MINUTES}"),  # Every N minutes
    },
    "update-server-status": {
        "task": "app.tasks.monitoring.update_server_status",
        "schedule": crontab(minute="*/5"),  # Every 5 minutes
    },
    "check-user-balances": {
        "task": "app.tasks.billing.check_user_balances",
        "schedule": crontab(minute="*/10"),  # Every 10 minutes
    },
}
