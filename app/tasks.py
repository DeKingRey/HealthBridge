from flask_mail import Message
from app import mail, db
from celery_worker import celery
from config import (APPOINTMENT_ID, MEDICATION_ID)


@celery.task
def send_reminder_email(to, subject, body, reminder):
    msg = Message(
        subject=subject,
        recipients=[to],
        body=body
    )
    print("EMAIL SENT")
    mail.send(msg)

    if type_id == APPOINTMENT_ID:
        db.session.delete
