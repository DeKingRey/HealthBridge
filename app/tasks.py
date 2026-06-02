from flask_mail import Message
from app.extensions import db, mail
from celery_worker import celery
from config import (APPOINTMENT_ID, MEDICATION_ID, UPCOMING_ID,
                    OVERDUE_ID)
from app.models import Reminder
from datetime import timedelta, timezone
from zoneinfo import ZoneInfo


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

        # Sets scheduled time to next day and prevents DST errors
        nz_tz = ZoneInfo("Pacific/Auckland")
        current_nz = (reminder.scheduled_time.replace(tzinfo=timezone.utc).
                      astimezone(nz_tz))
        next_nz = current_nz + timedelta(days=1)
        reminder.scheduled_time = next_nz.astimezone(timezone.utc)
    db.session.commit()


@celery.task
def reset_medication_statuses():
    # Resets all medication statuses to upcoming at midnight
    meds = Reminder.query.filter_by(type_id=MEDICATION_ID).all()

    for med in meds:
        med.status_id = UPCOMING_ID
    db.session.commit()
