from celery import Celery
from app import create_app

app = create_app()

celery = Celery(
                app.import_name,
                broker="redis://localhost:6379/0",
                backend="redis://localhost:6379/0",
                include=["app.tasks"]
                )

celery.conf.timezone = "UTC"
celery.conf.enable_utc = True


# Tasks must be run with app context to use mail and db
class ContextClass(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)


celery.Task = ContextClass
