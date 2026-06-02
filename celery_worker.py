from celery import Celery
from celery.schedules import crontab
from app import create_app

app = create_app()

celery = Celery(
                app.import_name,
                broker="redis://localhost:6379/0",
                backend="redis://localhost:6379/0",
                include=["app.tasks"]
                )

# App is NZ only
celery.conf.timezone = "Pacific/Auckland"
celery.conf.enable_utc = True


# Tasks must be run with app context to use mail and db
class ContextClass(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)


celery.Task = ContextClass

# Schedules med reminders to reset to upcoming at midnight
celery.conf.beat_schedule = {
    "reset-meds-midnight": {
        "task": "app.tasks.reset_medication_statuses",
        "schedule": crontab(hour=0, minute=0),
    },
}
