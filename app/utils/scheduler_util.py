"""from app.services.slot_service import SlotService
from app.services.appointment_service import AppointmentService
from apscheduler.schedulers.background import BackgroundScheduler


def start_scheduler():
    scheduler = BackgroundScheduler()
    
    if not scheduler.running:
        scheduler.add_job(SlotService.expire_old_slots, "interval", minutes=10)
        scheduler.add_job(AppointmentService.expire_old_appointments, "interval", minutes=10)
        scheduler.start()
        print("started")
    return scheduler
"""


from apscheduler.schedulers.background import BackgroundScheduler
#from app import create_app
from app.services.slot_service import SlotService
from app.services.appointment_service import AppointmentService
from datetime import datetime

#app = create_app()  # Import your Flask app factory

def start_scheduler(app):
    scheduler = BackgroundScheduler()

    # Wrap job calls in app.app_context()
    def expire_slots_job():
        with app.app_context():
            SlotService.expire_old_slots()

    def expire_appointments_job():
        with app.app_context():
            AppointmentService.expire_old_appointments()

    scheduler.add_job(
        expire_slots_job,
        trigger="interval",
        minutes=10,
        id="expire_slots",
        next_run_time=datetime.now()
    )

    scheduler.add_job(
        expire_appointments_job,
        trigger="interval",
        minutes=10,
        id="expire_appointments",
        next_run_time=datetime.now()
    )

    scheduler.start()
    print("✅ Scheduler started")
    return scheduler
