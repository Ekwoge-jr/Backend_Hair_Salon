from app.models.repositories.service_repo import ServiceRepository
from app.models.entities.service import serviceEntity


class ServiceService:

    @staticmethod
    def create_service(name, description, price, duration):
        service = serviceEntity(
            name = name,
            description = description,
            price = price,
            duration = duration
        )
        return ServiceRepository.save_service(service)
    

    @staticmethod
    def get_all_services():
        return ServiceRepository.get_all_services()
    

    @staticmethod
    def update_service(service_id, name=None, description=None, price=None, duration=None):
        service = ServiceRepository.get_service_by_id(service_id)
        if not service:
            return None
        
        if name:
            service.name = name
        if description:
            service.description = description
        if price:
            service.price = price
        if duration:
            service.duration = duration

        return ServiceRepository.update_service(service_id, service.name, service.description, service.price, service.duration)
    

    @staticmethod
    def delete_service(service_id):
        return ServiceRepository.delete_service(service_id)
        