from flask_mail import Message
from app import mail
from celery_worker import celery


@celery.task
def send_reminder_email(to, subject, body):
    msg = Message(
        subject=subject,
        recipients=[to],
        body=body
    )

    mail.send(msg)