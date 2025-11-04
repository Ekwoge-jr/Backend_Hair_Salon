from app.services.slot_service import SlotService
from app.services.appointment_service import AppointmentService
from apscheduler.schedulers.background import BackgroundScheduler


def start_scheduler():
    scheduler = BackgroundScheduler()
    
    if not scheduler.running:
        scheduler.add_job(SlotService.expire_old_slots, "interval", minutes=10)
        scheduler.add_job(AppointmentService.expire_old_appointments, "interval", minutes=10)
        scheduler.start()
    return scheduler