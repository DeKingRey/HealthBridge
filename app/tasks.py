from flask_mail import Message
from app.extensions import db, mail
from celery_worker import celery
from config import (APPOINTMENT_ID, MEDICATION_ID, UPCOMING_ID,
                    OVERDUE_ID)
from app.models import Reminder
from datetime import timedelta


@celery.task
def send_reminder_email(to, subject, body, reminder_id):
    msg = Message(
        subject=subject,
        recipients=[to],
        body=body
    )

    mail.send(msg)

    reminder = Reminder.query.get(reminder_id)

    if reminder.type_id == APPOINTMENT_ID:
        db.session.delete(reminder)
    elif reminder.type_id == MEDICATION_ID:
        # Sets to overdue until taken
        reminder.status_id = OVERDUE_ID
        # Sets schduled time to next day
        reminder.scheduled_time += timedelta(days=1)
    db.session.commit()


@celery.task
def reset_medication_statuses():
    # Resets all medication statuses to upcoming at midnight
    meds = Reminder.query.filter_by(type_id=MEDICATION_ID).all()

    for med in meds:
        med.status_id = UPCOMING_ID
    db.session.commit()
