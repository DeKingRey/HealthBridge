from flask_mail import Message
from app.extensions import db, mail
from celery_worker import celery
from config import (APPOINTMENT_ID, MEDICATION_ID)
from app.models import Reminder
from datetime import timedelta


@celery.task
def send_reminder_email(to, subject, body, reminder_id):
    msg = Message(
        subject=subject,
        recipients=[to],
        body=body
    )
    print("EMAIL SENT")
    mail.send(msg)

    reminder = Reminder.query.get(reminder_id)

    if reminder.type_id == APPOINTMENT_ID:
        db.session.delete(reminder)
    elif reminder.type_id == MEDICATION_ID:
        reminder.scheduled_time += timedelta(days=1)
    db.session.commit()
